function convertToGroupInvitationLink(groupId) {
    //TODO: change to https
    return "http://" + location.host + "/event/registerattendee/" + groupId;
}
function copyText(text) {
    navigator.clipboard.writeText(text);
    alert("Text copied!");
}

function sendGroupSyncState(event_id, group_id, state) {
    console.log(event_id);
    console.log(group_id);
    console.log(state);

    req = new XMLHttpRequest();
    req.open("POST", "/event/" + event_id + "/admin/groupsyncstate");
    req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    req.send(JSON.stringify({"group_id": group_id, state: state}));

}