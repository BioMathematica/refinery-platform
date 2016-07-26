/**
 * Created by scott on 7/15/16.
 */
'use strict';

function dataUploadTutorialCtrl ($scope, tutorialPageNavigation) {
  var stepText = $scope.refineryTutorialSteps.DATA_UPLOAD_TUTORIAL;

  $scope.dataUploadCompletedEvent = function () {
    tutorialPageNavigation.setData($scope.dataUploadKey, true);
    document.getElementById('dataUploadTutorialStep0').click();
  };

  $scope.dataUploadExitEvent = function () {
  };

  $scope.dataUploadChangeEvent = function () {
  };

  $scope.dataUploadBeforeChangeEvent = function () {

  };

  $scope.dataUploadAfterChangeEvent = function () {
  };


  $scope.dataUploadIntroOptions = {
    showStepNumbers: false,
    showBullets: false,
    exitOnOverlayClick: false,
    exitOnEsc: false,
    nextLabel: '<strong><i class="fa fa-arrow-right"></i></strong>',
    prevLabel: '<strong><i class="fa fa-arrow-left"></i></strong>',
    skipLabel: '<strong><i class="fa fa-times"></i></strong>',
    doneLabel: 'Proceed to <b>Upload</b> page'
  };

  setTimeout(function () {
    $scope.dataUploadIntroOptions.steps = [
      {
        element: document.querySelector('#dataUploadTutorialStep0'),
        intro: '<div class="text-align-center">' + stepText.STEP0 + '</div>',
        position: 'bottom'
      }
    ];
  }, 500);
}

angular
  .module('refineryDashboard')
  .controller('dataUploadTutorialCtrl', [
    '$scope',
    'tutorialPageNavigation',
    dataUploadTutorialCtrl
  ]);
