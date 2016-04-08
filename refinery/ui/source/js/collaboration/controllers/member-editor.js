'use strict';

function MemberEditorCtrl ($uibModalInstance, groupDataService, groupMemberService, member) {
  var that = this;
  that.$uibModalInstance = $uibModalInstance;
  that.groupDataService = groupDataService;
  that.groupMemberService = groupMemberService;
  that.member = member;
}

MemberEditorCtrl.prototype.promote = function () {
  var that = this;

  this.groupMemberService.add({
    uuid: that.groupDataService.activeGroup.manager_group_uuid,
    user_id: that.member.user_id
  }).$promise.then(
    function (data) {
      that.groupDataService.update();
      that.$uibModalInstance.dismiss();
    }
  ).catch(function (error) {
    console.error(error);
    bootbox.alert('Could not promote member');
  });
};

MemberEditorCtrl.prototype.demote = function () {
  var that = this;

  that.groupMemberService.remove({
    uuid: that.groupDataService.activeGroup.manager_group_uuid,
    userId: that.member.user_id
  }).$promise.then(
    function (data) {
      that.groupDataService.update();
      that.$uibModalInstance.dismiss();
    }
  ).catch(function (error) {
    console.error(error);
    bootbox.alert('Are you the only member or manager left?');
  });
};

MemberEditorCtrl.prototype.remove = function () {
  var that = this;

  that.groupMemberService.remove({
    uuid: that.groupDataService.activeGroup.uuid,
    userId: that.member.user_id
  }).$promise.then(
    function (data) {
      that.groupDataService.update();
      that.$uibModalInstance.dismiss();
    }
  ).catch(function (error) {
    console.error(error);
    bootbox.alert('Are you the only member or manager left?');
  });
};

angular
  .module('refineryCollaboration')
  .controller('MemberEditorCtrl', [
    '$uibModalInstance',
    'groupDataService',
    'groupMemberService',
    'member',
    MemberEditorCtrl
  ]);
