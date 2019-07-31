// custom javascript

var opts = {
  angle: -0.02, // The span of the gauge arc
  lineWidth: 0.2, // The line thickness
  radiusScale: 0.94, // Relative radius
  pointer: {
    length: 0.65, // // Relative to gauge radius
    strokeWidth: 0.042, // The thickness
    color: '#000000' // Fill color
  },
  limitMax: false,     // If false, max value increases automatically if value > maxValue
  limitMin: false,     // If true, the min value of the gauge will be fixed
  colorStart: '#6FADCF',   // Colors
  colorStop: '#8FC0DA',    // just experiment with them
  strokeColor: '#E0E0E0',  // to see which ones work best for you
  generateGradient: true,
  highDpiSupport: true,     // High resolution support

};
var target = document.getElementById('foo'); // your canvas element
var gauge = new Gauge(target).setOptions(opts); // create sexy gauge!
gauge.maxValue = 3000; // set max gauge value
gauge.setMinValue(0);  // Prefer setter over gauge.minValue = 0
gauge.animationSpeed = 47; // set animation speed (32 is default value)
gauge.set(1475); // set actual value
