'use strict';

angular.module('appApp')
  .controller('MainCtrl', ['$scope', 'syncData', 'snapshot', 'dateFilter', '$q', function ($scope, syncData, snapshot, dateFilter, $q) {

    $scope.ght = syncData('AB', 1);
    $scope.ghtStatus = syncData('AB/status', 1);
    $scope.recentErrors = syncData('/errors', 10);
    $scope.ghtReadings = 12;

    $scope.lt = syncData('AA', 1);
    $scope.ltStatus = syncData('AA/status', 1);
    $scope.ltReadings = 6;

    $scope.getDate = function (timestamp) {
      var date = new Date(parseFloat(timestamp) * 1000);
      return date;
    };

    $scope.movementDirection = function (sensor) {
      // determine the direction the temperature is going in...
      var direction = 'warmer (static) ' + sensor;

      return direction;
    };

    $scope.getChartData = function (sensor, dataPoints) {
      // get data for last dataPoints readings
      // combine all sensors on one chart (for now)
      // data = {
      //  series: [
      //      "sensor AA",
      //      "sensor BB"
      //  ],
      //  data: [
      //      {x: "date",
      //       y: 23.25,
      //       tooltip: "23.25ºC"
      //      }
      //  ]
      // }
      var deferred = $q.defer();
      var chartData = {};
      chartData.series = ['temperature'];
      chartData.data = [];
      snapshot(sensor, dataPoints, 0, function (data) {
        console.log('snapshot callback called');
        data.forEach(function (d) {
          var dp = {};
          var dateLabel = dateFilter(new Date(parseFloat(d.child('time').val()) * 1000), 'yyyy-MM-dd HH:mm:ss');
          dp.x = dateLabel;
          dp.y = [];
          var reading = d.child('responseValue').val();
          dp.y.push(parseFloat(reading));
          dp.tooltip = reading + 'ºC - ' + dateLabel;
          chartData.data.push(dp);
        });
        deferred.resolve(chartData);
      });

      return deferred.promise;
    };

    $scope.getChartConfig = function (readings, minutes) {

      var deferred = $q.defer();
      var config = {
        labels: false,
        tooltips: true,
        click: function (d) {
          console.log(d);
        },
        title: 'Temperature - last ' + (readings * minutes / 60) + ' hours from ' + dateFilter(new Date(), 'yyyy-MM-dd HH:mm:ss'),
        legend: {
          display: false,
          position: 'left'
        },
        height: '600px'
      };
      deferred.resolve(config);
      return deferred.promise;

    };
    // 288 * 5 min = 24 hours
    $scope.$watch('[ght, ghtReadings]', function () {
      //$scope.chartData1 = {};
      $scope.getChartData('AB', $scope.ghtReadings).then(function (data) {
        $scope.chartData1 = data;
      }); // taken every 5 mins
      $scope.getChartConfig($scope.ghtReadings, 5).then(function (data) {
        $scope.chartConfig1 = data;
      });
    }, true);

    $scope.$watch('[lt, ltReadings]', function () {
      //$scope.chartData2 = {};
      $scope.getChartData('AA', $scope.ltReadings).then(function (data) {
        $scope.chartData2 = data;
      }); // taken every 10 mins
      $scope.getChartConfig($scope.ltReadings, 10).then(function (data) {
        $scope.chartConfig2 = data;
      });
    }, true);

    $scope.chartType = 'line';

  }]);
