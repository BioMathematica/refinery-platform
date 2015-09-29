angular
  .module('refineryAnalysisLaunch')
  .directive(
    'rfAnalysisLaunchModalDetail',
    [
      '$log',
      '$modal',
      rfAnalysisLaunchModalDetail
    ]
  );

function rfAnalysisLaunchModalDetail( $log, $modal) {
  "use strict";
    return {
    restrict: 'AE',
    templateUrl: '/static/partials/analysis/partials/analysis-launch-modal-detail.html',
    };
}
