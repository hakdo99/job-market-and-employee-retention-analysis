#*************************************
# Created by: Rovenna Chu (ytc17@sfu.ca)
# Purpose: this is for skill extraction from consolidated parquet files containing all job posts to list of skills for each post and job title
# This py file contains all classes and functions for building the text classification model with bert embeddings
# example usage: from job_skill_extraction_model import PaddingInputExample
#*************************************

# Loading the model building functions
# Upgrade from TF1 to TF2 for bert implementation
# tensorflow_version 2.8.0

# Prerequisite
#pip install contractions
#pip install bert-for-tf2
#pip install tqdm
#pip install tensorflow_hub
#pip install --upgrade tensorflow

from tqdm import tqdm_notebook

import tensorflow as tf
import tensorflow_hub as hub
import bert
from tensorflow import keras
from tensorflow.keras.layers import Input

import pandas as pd
import numpy as np

# 1. Tokenization

class PaddingInputExample(object):
    """Fake example so the num input examples is a multiple of the batch size.
  When running eval/predict on the TPU, we need to pad the number of examples
  to be a multiple of the batch size, because the TPU requires a fixed batch
  size. The alternative is to drop the last batch, which is bad because it means
  the entire output data won't be generated.
  We use this class instead of `None` because treating `None` as padding
  battches could cause silent errors.
  """
    pass

class InputExample(object):
    """A single training/test example for simple sequence classification."""

    def __init__(self, guid, text_a, text_b=None, label=None):
        """Constructs a InputExample.
    Args:
      guid: Unique id for the example.
      text_a: string. The untokenized text of the first sequence. For single
        sequence tasks, only this sequence must be specified.
      text_b: (Optional) string. The untokenized text of the second sequence.
        Only must be specified for sequence pair tasks.
      label: (Optional) string. The label of the example. This should be
        specified for train and dev examples, but not for test examples.
    """
        self.guid = guid
        self.text_a = text_a
        self.text_b = text_b
        self.label = label

def create_tokenizer_from_hub_module():
    """Get the vocab file and casing info from the Hub module."""
    BertTokenizer = bert.bert_tokenization.FullTokenizer
    bert_layer = hub.KerasLayer("https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/1",
                                trainable=False)
    vocabulary_file = bert_layer.resolved_object.vocab_file.asset_path.numpy()
    to_lower_case = bert_layer.resolved_object.do_lower_case.numpy()
    tokenizer = BertTokenizer(vocabulary_file, to_lower_case)

    return tokenizer

def convert_single_example(tokenizer, example, max_seq_length=256):
    """Converts a single `InputExample` into a single `InputFeatures`."""

    if isinstance(example, PaddingInputExample):
        input_ids = [0] * max_seq_length
        input_mask = [0] * max_seq_length
        segment_ids = [0] * max_seq_length
        label = 0
        return input_ids, input_mask, segment_ids, label

    tokens_a = tokenizer.tokenize(example.text_a)
    if len(tokens_a) > max_seq_length - 2:
        tokens_a = tokens_a[0 : (max_seq_length - 2)]

    tokens = []
    segment_ids = []
    tokens.append("[CLS]")
    segment_ids.append(0)
    for token in tokens_a:
        tokens.append(token)
        segment_ids.append(0)
    tokens.append("[SEP]")
    segment_ids.append(0)

    input_ids = tokenizer.convert_tokens_to_ids(tokens)

    # The mask has 1 for real tokens and 0 for padding tokens. Only real
    # tokens are attended to.
    input_mask = [1] * len(input_ids)

    # Zero-pad up to the sequence length.
    while len(input_ids) < max_seq_length:
        input_ids.append(0)
        input_mask.append(0)
        segment_ids.append(0)

    assert len(input_ids) == max_seq_length
    assert len(input_mask) == max_seq_length
    assert len(segment_ids) == max_seq_length

    return input_ids, input_mask, segment_ids, example.label

def convert_examples_to_features(tokenizer, examples, max_seq_length=256):
    """Convert a set of `InputExample`s to a list of `InputFeatures`."""

    input_ids, input_masks, segment_ids, labels = [], [], [], []
    for example in tqdm_notebook(examples, desc="Converting examples to features"):
        input_id, input_mask, segment_id, label = convert_single_example(
            tokenizer, example, max_seq_length
        )
        input_ids.append(input_id)
        input_masks.append(input_mask)
        segment_ids.append(segment_id)
        labels.append(label)
    return (
        np.array(input_ids),
        np.array(input_masks),
        np.array(segment_ids),
        np.array(labels).reshape(-1, 1),
    )

def convert_text_to_examples(texts, labels):
    """Create InputExamples"""
    InputExamples = []
    for text, label in zip(texts, labels):
        InputExamples.append(
            InputExample(guid=None, text_a=" ".join(str(text)), text_b=None, label=label)
        )
    return InputExamples

# 2. Embedding
class BertModel(object):
    
    def __init__(self):
        
        self.max_len = 18
        bert_path = "https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/1"
        FullTokenizer=bert.bert_tokenization.FullTokenizer
        
        self.bert_module = hub.KerasLayer(bert_path,trainable=True)

        self.vocab_file = self.bert_module.resolved_object.vocab_file.asset_path.numpy()

        self.do_lower_case = self.bert_module.resolved_object.do_lower_case.numpy()

        self.tokenizer = FullTokenizer(self.vocab_file,self.do_lower_case)
        
    def get_masks(self,tokens, max_seq_length):
        return [1]*len(tokens) + [0] * (max_seq_length - len(tokens))

    def get_segments(self,tokens, max_seq_length):
        """Segments: 0 for the first sequence, 1 for the second"""
        segments = []
        current_segment_id = 0
        for token in tokens:
            segments.append(current_segment_id)
            if token == "[SEP]":
                current_segment_id = 1
        return segments + [0] * (max_seq_length - len(tokens))
    
    def get_ids(self,tokens, tokenizer, max_seq_length):
        """Token ids from Tokenizer vocab"""
        token_ids = tokenizer.convert_tokens_to_ids(tokens,)
        input_ids = token_ids + [0] * (max_seq_length-len(token_ids))
        return input_ids
    def create_single_input(self,sentence,maxlen):

        stokens = self.tokenizer.tokenize(sentence)

        stokens = stokens[:maxlen]

        stokens = ["[CLS]"] + stokens + ["[SEP]"]

        ids = self.get_ids(stokens, self.tokenizer, self.max_len)
        masks = self.get_masks(stokens, self.max_len)
        segments = self.get_segments(stokens, self.max_len)

        return ids,masks,segments

    def create_input_array(self,sentences):
        
        input_ids, input_masks, input_segments = [], [], []

        for sentence in tqdm_notebook(sentences,position=0, leave=True):
            ids,masks,segments=self.create_single_input(sentence,self.max_len-2)

            input_ids.append(ids)
            input_masks.append(masks)
            input_segments.append(segments)
            
        tensor = [np.asarray(input_ids, dtype=np.int32), 
                np.asarray(input_masks, dtype=np.int32), 
                np.asarray(input_segments, dtype=np.int32)]
        return tensor
"""
class PreprocessingBertData():
    
    def prepare_data_x(self,train_sentences):
        x = bert_model_obj.create_input_array(train_sentences)
        return x
    
    def prepare_data_y(self,train_labels):
        y = list()
        for item in train_labels:
            label = item
            y.append(label)
        y = np.array(y)
        return y
"""
# 3. Model Building
class NetworkModel():
    def __init__(self):
        self.model = None        
        #self.train_data = [train_input_ids, train_input_masks, train_segment_ids]
        #self.train_labels = train_labels
        #self.test_data = [test_input_ids, test_input_masks, test_segment_ids]
        #self.test_labels = test_labels
        
    def bert_model(self,bert_model_obj, max_seq_length): 
        in_id = Input(shape=(max_seq_length,), dtype=tf.int32, name="input_ids")
        in_mask = Input(shape=(max_seq_length,), dtype=tf.int32, name="input_masks")
        in_segment = Input(shape=(max_seq_length,), dtype=tf.int32, name="segment_ids")
        
        bert_inputs = [in_id, in_mask, in_segment]

        pooled_output, sequence_output = bert_model_obj.bert_module(bert_inputs)
        """
        #x = tf.keras.layers.GlobalAveragePooling1D()(sequence_output)
        x = tf.keras.layers.SpatialDropout1D(0.2)(sequence_output)
        x = tf.keras.layers.LSTM(64, dropout=0.2, recurrent_dropout=0.2),
        pred = tf.keras.layers.Dense(units=1, activation='sigmoid')(x)
        optimizer = tf.keras.optimizers.Adam(lr=0.00001)
        self.model = tf.keras.models.Model(inputs=bert_inputs, outputs=pred)
        self.model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
        """
        
        x = tf.keras.layers.GlobalAveragePooling1D()(sequence_output)
        x = tf.keras.layers.Dense(128, activation='relu')(x)
        x = tf.keras.layers.Dense(64, activation='relu')(x)
        x = tf.keras.layers.Dense(32, activation='relu')(x)
        x = tf.keras.layers.Dense(24, activation='tanh')(x)
        x = tf.keras.layers.Dense(12, activation='relu')(x)
        pred = tf.keras.layers.Dense(1, activation='softplus')(x)
        optimizer = tf.keras.optimizers.Adam(lr=0.00001)
        self.model = tf.keras.models.Model(inputs=bert_inputs, outputs=pred)
        self.model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
        
        
        
        self.model.summary()
    
    def model_train(self,batch_size,num_epoch):
        print("Fitting to Model")
        
        self.model.fit(self.train_data,self.train_labels,epochs=num_epoch,batch_size=batch_size,validation_split=0.2,shuffle=True)
        
        print("Model Training Complete.")
    
    def model_test(self):
        print("Model Testing on Unseen Data")

        self.model.evaluate(self.test_data, self.test_labels)
        
        print("Model Testing Complete.")

    def save_model(self,model_folder,model_name):    
        self.model.save(model_name+".h5", overwrite=True, include_optimizer=True)
        print("Model saved to Model folder.")

    def get_model(self):    
        return self.model
    
    def load_weights(self, path):
        self.model.load_weights(path)
        print("Model weights loaded.")