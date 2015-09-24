angular.module('refineryAnalysis')
  .controller('AnalysisCtrl',
  [
    '$scope',
    '$log',
    'analysisConfigService',
    AnalysisCtrl
  ]
);


function AnalysisCtrl($scope, $log, analysisConfigService ) {
    "use strict";

  var vm = this;

  $scope.$onRootScope('nodeSetChangedEvent', function(event, currentNodeSet) {
    analysisConfigService.setAnalysisConfig(
      {
        nodeSetUuid: currentNodeSet.uuid,
        nodeRelationshipUuid: null
      });
    });

  $scope.$onRootScope('nodeRelationshipChangedEvent', function(event, currentNodeRelationship) {
    if (!currentNodeRelationship) {
      analysisConfigService.setAnalysisConfig(
      {
        nodeSetUuid: null,
        nodeRelationshipUuid: null
      });
    }
    else {
      analysisConfigService.setAnalysisConfig(
      {
        nodeSetUuid: null,
        nodeRelationshipUuid: currentNodeRelationship.uuid
      });
    }
  });
}
