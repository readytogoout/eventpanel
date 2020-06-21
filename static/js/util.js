function convertToGroupInvitationLink(groupId) {
    //TODO: change to https
    return "http://" + location.host + "/event/registerattendee/" + groupId;
}
function copyText(text) {
    navigator.clipboard.writeText(text);
    alert("Text copied!");
}