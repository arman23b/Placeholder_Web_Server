$(document).ready(function () {

    addRoomListener();
    addStationListener();
    addItemListener();

    addLoadingUnregistered();

});


function addRoomListener() {
    $( "#room-dialog" ).dialog({
        autoOpen: false,
        modal: true
    });
    $("#newRoomOpenDialog").click(function () {
        $("#room-dialog").dialog("open");
    });
    $("#newRoomButton").click(function () {
        var newRoomName = $("#newRoomName").val().toLowerCase();
        if (newRoomName != "") addNewRoom(newRoomName);
        $("#newRoomName").val("");
        $("#room-dialog").dialog("close");
    });
}


function addNewRoom(newRoomName) {
    var ul = $("#rooms-list");
    ul.append("<li class='popover-item'><a class='text-link'>" + newRoomName + "</a></li>");
    $.ajax({
        'url': 'addRoom', 
        'type': 'POST',
        'dataType': 'json',
        'data': { name : newRoomName },
        'success': function(data) {
        },
        'error': function() {
            console.error("Error");
        }
    });
    $("#roomOptions").append("<option class='text'>" + newRoomName + "</option>");
}


function addStationListener() {
    $( "#station-dialog" ).dialog({
        autoOpen: false,
        modal: true
    });
    $("#newStationOpenDialog").click(function () {
        $("#station-dialog").dialog("open");
    });
    $("#newStationButton").click(function () {
        var newStationName = $("#newStationName").val().toLowerCase();
        var newStationIp = $("#newStationIp").val();
        var newStationRoom = $("#roomOptions option:selected").text();
        if (newStationName != "" && newStationIp != "") {
            addNewStation(newStationName, newStationIp, newStationRoom);
        }
        $("#newStationName").val("");
        $("#newStationIp").val("");
        $("#station-dialog").dialog("close");
        removeElementFromList(newStationIp, $("#unregisteredStations-list"), ".ipAddress");
    });
}


function addNewStation(name, ip, room) {
    var ul = $("#stations-list");
    appendNewStation(ul, name, ip, room);
    $.ajax({
        'url': 'addStation', 
        'type': 'POST',
        'dataType': 'json',
        'data': { name : name, ip : ip, room : room },
        'success': function(data) {
        },
        'error': function() {
            console.error("Error");
        }
    });
}


function addItemListener() {
    $( "#item-dialog" ).dialog({
        autoOpen: false,
        modal: true
    });
    $("#newItemOpenDialog").click(function () {
        $("#item-dialog").dialog("open");
    });
    $("#newItemButton").click(function () {
        var newItemName = $("#newItemName").val().toLowerCase();
        var newItemBeaconId = $("#newItemBeaconId").val();
        var newItemRoom = $("#newItemRoom").val();
        if (newItemName != "" && newItemBeaconId != "") {
            addNewItem(newItemName, newItemBeaconId, newItemRoom);
        }
        $("#newItemName").val("");
        $("#newItemBeaconId").val("");
        $("#item-dialog").dialog("close");
        removeElementFromList(newItemBeaconId, $("#unregisteredItems-list"), ".beaconId");
    });
}


function addNewItem(name, beaconId, room) {
    var ul = $("#items-list");
    appendNewItem(ul, name, beaconId, room);
    $.ajax({
        'url': 'addItem', 
        'type': 'POST',
        'dataType': 'json',
        'data': { name : name, beaconId : beaconId },
        'success': function(data) {
        },
        'error': function() {
            console.error("Error");
        }
    });
}


function addLoadingUnregistered() {
    setInterval(function () {
        $.ajax({
            'url': 'loadUnregistered', 
            'type': 'POST',
            'dataType': 'json',
            'data': {},
            'success': function(data) {
                var unregisteredIpAddresses = data["unregisteredIpAddresses"];
                var unregisteredBeaconIds = data["unregisteredBeaconIds"];
                updateUnregisteredStations(unregisteredIpAddresses);
                updateUnregisteredItems(unregisteredBeaconIds);
            },
            'error': function() {
                console.error("Error");
            }
        }); 
    }, 5000);
}


function updateUnregisteredStations(ipAddresses) {
    var ul = $("#unregisteredStations-list");
    ul.empty();
    for (var i = 0; i < ipAddresses.length; i++) {
        appendNewStation(ul, "-------", ipAddresses[i]["ipAddress"], "-------");
    }
    $("a.unregistered-station").click(function () {
        $("#station-dialog").dialog("open");
        var ipAddress = $(this).find(".ipAddress").html();
        $("#newStationIp").val(ipAddress);
    });
}


function updateUnregisteredItems(beaconIds) {
    var ul = $("#unregisteredItems-list");
    ul.empty();
    for (var i = 0; i < beaconIds.length; i++) {
        appendNewItem(ul, "-------", beaconIds[i]["beaconId"], beaconIds[i]["room"]);
    }
    $("a.unregistered-item").click(function () {
        $("#item-dialog").dialog("open");
        var beaconId = $(this).find(".beaconId").html();
        $("#newItemBeaconId").val(beaconId);
        var room = $(this).find(".item-room").html();
        $("#newItemRoom").val(room);
    });
}


function removeElementFromList(element, list, className) {
    list.find("li").each(function () {
        var a = $(this).find("a");
        if (a.find(className).html() == element) {
            $(this).remove();
        }
    });
}


function appendNewStation(ul, name, ip, room) {
    ul.append('<li class="popover-item">' +
        '<a class="text-link unregistered-station">' +
        '<div class="name">' + name + '</div>' + 
        '<div class="info ipAddress">' + ip + '</div>' + 
        '<div class="info">&nbsp; | &nbsp;</div>' + 
        '<div class="info station-room">' + room + '</div>' + 
        '</a>' + 
        '</li>');
}


function appendNewItem(ul, name, beaconId, room) {
    ul.append('<li class="popover-item">' +
        '<a class="text-link unregistered-item">' +
        '<div class="name">' + name + '</div>' + 
        '<div class="info beaconId">' + beaconId + '</div>' + 
        '<div class="info">&nbsp; | &nbsp;</div>' + 
        '<div class="info item-room">' + room + '</div>' + 
        '</a>' + 
        '</li>');
}