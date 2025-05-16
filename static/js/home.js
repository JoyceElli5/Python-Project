document.addEventListener('DOMContentLoaded', function() {
	// Initialize AOS
	AOS.init({
	  duration: 800,
	  once: true,
	  mirror: false
	});
  
	// Budget Chart
	const ctx = document.getElementById('budgetChart').getContext('2d');
	
	// Chart gradient
	const gradient = ctx.createLinearGradient(0, 0, 0, 200);
	gradient.addColorStop(0, 'rgba(225, 29, 72, 0.5)');
	gradient.addColorStop(1, 'rgba(225, 29, 72, 0.0)');
	
	// Chart data
	const data = {
	  labels: ['18 dec', '25 dec', '1 jan', '8 jan', '15 jan', '22 jan', '29 jan'],
	  datasets: [{
		label: 'Budget',
		data: [2500, 3000, 2000, 2500, 1500, 3000, 2500],
		borderColor: '#e11d48',
		backgroundColor: gradient,
		borderWidth: 2,
		tension: 0.4,
		fill: true,
		pointBackgroundColor: '#fff',
		pointBorderColor: '#e11d48',
		pointBorderWidth: 2,
		pointRadius: 0,
		pointHoverRadius: 4
	  }]
	};
	
	// Chart config
	const config = {
	  type: 'line',
	  data: data,
	  options: {
		responsive: true,
		maintainAspectRatio: false,
		plugins: {
		  legend: {
			display: false
		  },
		  tooltip: {
			backgroundColor: 'rgba(255, 255, 255, 0.8)',
			titleColor: '#333',
			bodyColor: '#333',
			borderColor: '#eee',
			borderWidth: 1,
			cornerRadius: 8,
			displayColors: false,
			callbacks: {
			  title: function(context) {
				return context[0].label;
			  },
			  label: function(context) {
				return `$${context.raw.toLocaleString()}`;
			  }
			}
		  }
		},
		scales: {
		  x: {
			display: false,
			grid: {
			  display: false
			}
		  },
		  y: {
			display: true,
			grid: {
			  color: '#f5f5f7',
			  drawBorder: false
			},
			ticks: {
			  display: true,
			  padding: 10,
			  color: '#666',
			  font: {
				size: 10
			  },
			  callback: function(value) {
				if (value % 1000 === 0) {
				  return value / 1000 + 'k';
				}
				return '';
			  }
			},
			min: 0,
			max: 6000,
			stepSize: 1000
		  }
		},
		elements: {
		  point: {
			radius: 0,
			hoverRadius: 6
		  }
		},
		interaction: {
		  mode: 'index',
		  intersect: false
		}
	  }
	};
	
	// Create chart
	const budgetChart = new Chart(ctx, config);
	
	// Highlight the peak point (8 jan)
	setTimeout(() => {
	  budgetChart.setActiveElements([{ datasetIndex: 0, index: 3 }]);
	  budgetChart.update();
	}, 1000);
	
	// Category pills interaction
	const pills = document.querySelectorAll('.pill');
	pills.forEach(pill => {
	  pill.addEventListener('click', () => {
		pills.forEach(p => p.classList.remove('active'));
		pill.classList.add('active');
	  });
	});
	
	// Dropdown interaction
	const dropdowns = document.querySelectorAll('.dropdown');
	dropdowns.forEach(dropdown => {
	  dropdown.addEventListener('mouseenter', () => {
		const menu = dropdown.querySelector('.dropdown-menu');
		if (menu) menu.style.display = 'block';
	  });
	  
	  dropdown.addEventListener('mouseleave', () => {
		const menu = dropdown.querySelector('.dropdown-menu');
		if (menu) menu.style.display = 'none';
	  });
	});
	
	// Responsive adjustments
	function handleResize() {
	  const container = document.querySelector('.container');
	  if (window.innerWidth < 1200) {
		container.style.height = 'auto';
	  } else {
		container.style.height = '540px';
	  }
	}
	
	window.addEventListener('resize', handleResize);
	handleResize();
  });