document.addEventListener('DOMContentLoaded', function () {
	/*const ctx = document.getElementById('predict_chart1');
	/*const myChart = new Chart(ctx, {
		type: 'bar',
		data: {
			labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
			datasets: [{
				label: '# of Votes',
				data: [12, 19, 3, 5, 2, 3],
				backgroundColor: [
					'rgba(255, 99, 132, 0.2)',
					'rgba(54, 162, 235, 0.2)',
					'rgba(255, 206, 86, 0.2)',
					'rgba(75, 192, 192, 0.2)',
					'rgba(153, 102, 255, 0.2)',
					'rgba(255, 159, 64, 0.2)'
				],
				borderColor: [
					'rgba(255, 99, 132, 1)',
					'rgba(54, 162, 235, 1)',
					'rgba(255, 206, 86, 1)',
					'rgba(75, 192, 192, 1)',
					'rgba(153, 102, 255, 1)',
					'rgba(255, 159, 64, 1)'
				],
				borderWidth: 1
			}]
		},
		options: {
			scales: {
				y: {
					beginAtZero: true
				}
			}
		}
	});*/

	const ctx1 = document.getElementById('retention_chart');
	const matchChart = new Chart(ctx1, {
		type: 'doughnut',
		data: {
			labels: ['stay %', 'leave %'],
			datasets: [
				{
				  label: "percentage",
				  backgroundColor: ["#EDECEC", "#8e5ea2"],
				  data: pred_json
				}
			]
		},
		options: {
			legend: {
				display: false
			},
			tooltips: {
				enabled: false
			},			
			plugins: {
				datalabels: {
					formatter: (value, ctx) => {
						let sum = 0;
						let dataArr = ctx.chart.data.datasets[0].data;
						dataArr.map(data => {
							sum += data;
						});
						let percentage = (value*100 / sum).toFixed(2)+"%";
						return percentage;
					},
					color: '#000',
				}
			}
		}
	});


}, false);
