var global_polling_freq = 5000;
var POLL_INTERVAL;
$(document).ready(function () {

    addRoomListener();
    addStationListener();
    addItemListener();
    addPollFreqListener();
    addLoadingUnregistered();
    addSearchListener();

});


function addPollFreqListener() {
    $( "#pollFreq-dialog" ).dialog({
        autoOpen: false,
        modal: true,
        closeOnEscape: true,
        close: function(ev, ui) {location.reload(true);}
    });
    $("#setPollFreq").click(function () {
        var newPollFreq = $("#newPollFreq").val();
        if (newPollFreq != "") {
          updatePollFreq(newPollFreq);
          $("#pollFreq-dialog").dialog("open");
        }
    });
}

function updatePollFreq(newPollFreq) {
  global_polling_freq = newPollFreq * 1000;
  clearInterval(POLL_INTERVAL);
  addLoadingUnregistered();
  $.ajax({
    'url': 'updatePollingFreq',
    'type': 'POST',
    'data': {pollFreq: newPollFreq},
    'success': function(data) {
    },
    'error': function() {
        console.error("Error");
    }
  });
}

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
        var newStationId = $("#newStationId").val();
        var newStationIp = $("#newStationIp").val();
        var newStationRoom = $("#roomOptions option:selected").text();
        if (newStationName != "" && newStationIp != "") {
            addNewStation(newStationName, newStationIp, newStationId, newStationRoom);
        }
        $("#newStationName").val("");
        $("#newStationIp").val("");
        $("#station-dialog").dialog("close");
        removeElementFromList(newStationIp, $("#unregisteredStations-list"), ".ipAddress");
    });
}


function addNewStation(name, ip, id, room) {
    var ul = $("#stations-list");
    appendNewStation(ul, name, ip, id, room);
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
    var loadUnregistered = function() {
        $.ajax({
            'url': 'loadUnregistered',
            'type': 'POST',
            'dataType': 'json',
            'data': {},
            'success': function(data) {
                var unregisteredIpAddresses = data["unregisteredIpAddresses"];
                var unregisteredBeaconIds = data["unregisteredBeaconIds"];
                var registeredBeaconIds = data["registeredBeaconIds"];
                updateUnregisteredStations(unregisteredIpAddresses);
                updateUnregisteredItems(unregisteredBeaconIds);
                updateRegisteredItems(registeredBeaconIds);
            },
            'error': function() {
                console.error("Error");
            }
        });
    };
    loadUnregistered();
    POLL_INTERVAL = setInterval(function () {
        loadUnregistered();
    }, global_polling_freq);
}


function updateUnregisteredStations(ipAddresses) {
    var ul = $("#unregisteredStations-list");
    ul.empty();
    for (var i = 0; i < ipAddresses.length; i++) {
        appendNewStation(ul, "-------", ipAddresses[i]["ipAddress"], ipAddresses[i]["id"], "-------");
    }
    $("a.unregistered-station").click(function () {
        $("#station-dialog").dialog("open");
        var ipAddress = $(this).find(".ipAddress").html();
        $("#newStationIp").prop("readonly", false);
        $("#newStationIp").val(ipAddress);
        $("#newStationIp").prop("readonly", true);
        var id = $(this).find(".id").html();
        $("#newStationId").prop("readonly", false);
        $("#newStationId").val(id);
        $("#newStationId").prop("readonly", true);
    });
}


function updateUnregisteredItems(beaconIds) {
    var ul = $("#unregisteredItems-list");
    ul.empty();
    for (var i = 0; i < beaconIds.length; i++) {
        appendNewItem(ul, "-------", beaconIds[i]["beaconId"], beaconIds[i]["room"], "unregistered-item");
    }
    $("a.unregistered-item").click(function () {
        $("#item-dialog").dialog("open");
        var beaconId = $(this).find(".beaconId").html();
        $("#newItemBeaconId").prop("readonly", false);
        $("#newItemBeaconId").val(beaconId);
        $("#newItemBeaconId").prop("readonly", true);
        var room = $(this).find(".item-room").html();
        $("#newItemRoom").prop("readonly", false);
        $("#newItemRoom").val(room);
        $("#newItemRoom").prop("readonly", true);
    });
}


function updateRegisteredItems(beaconIds) {
    var ul = $("#items-list");
    ul.empty();
    for (var i = 0; i < beaconIds.length; i++) {
        appendNewItem(ul, beaconIds[i]["name"], beaconIds[i]["beaconId"], beaconIds[i]["room"], "");
    }
}


function removeElementFromList(element, list, className) {
    list.find("li").each(function () {
        var a = $(this).find("a");
        if (a.find(className).html() == element) {
            $(this).remove();
        }
    });
}


function appendNewStation(ul, name, ip, id, room) {
    ul.append('<li class="popover-item">' +
        '<a class="text-link unregistered-station">' +
        '<div class="name">' + name + '</div>' +
        '<div class="info"> id: </div>' +
        '<div class="info id">' + id + '</div>' +
        '<div class="info">&nbsp; | &nbsp;</div>' +
        '<div class="info ipAddress">' + ip + '</div>' +
        '<div class="info">&nbsp; | &nbsp;</div>' +
        '<div class="info station-room">' + room + '</div>' +
        '</a>' +
        '</li>');
}


function appendNewItem(ul, name, beaconId, room, registeredClass) {
    if (registeredClass == 'undefined') {
        registeredClass = "";
    }
    ul.append('<li class="popover-item">' +
        '<a class="text-link ' + registeredClass + '"">' +
        '<div class="name">' + name + '</div>' +
        '<div class="info beaconId">' + beaconId + '</div>' +
        '<div class="info">&nbsp; | &nbsp;</div>' +
        '<div class="info item-room">' + room + '</div>' +
        '<div class="info searchBtnInfo"><button class="button-primary searchItemBtn">Search</button></div>' +
        '</a>' +
        '</li>');
    addSearchListener();
}

function addSearchListener() {
    /*
    $(document).on('click', '.searchItemBtn', function () {
        var uuid = $(this).parent().parent().find('.unregistered-item').find('.beaconId').text();
        console.log(uuid);
        updateSearchedBeacon(uuid);
    });
    */
    $('.searchItemBtn').click(function(e) {
        e.stopPropagation();
        var uuid = $(this).parent().parent().find('.beaconId').text();
        console.log(uuid);
        updateSearchedBeacon(uuid);
    })
}

function updateSearchedBeacon(uuid) {
  $.ajax({
    'url': 'broadcastUuid',
    'type': 'POST',
    'data': {uuid: uuid},
    'success': function(data) {
    },
    'error': function() {
        console.error("Error");
    }
  });
}

function addDeleteListner() {
  $('.deleteBtn').click(function(e) {
    e.stopPropagation();
  })
  var toDelete = $(this).parent();
  var list = toDelete.parent();
  list.removeElementFromList(toDelete);
}

function addUnregisterItemListner() {
  $('.unregisterItemBtn').click(function(e) {
    e.stopPropagation();
    var uuid = $(this).parent().parent().find('.beaconId').text();
    unregisterItem(uuid);
  })
}

function addUnregisterStationListner() {
  $('.unregisterStationBtn').click(function(e) {
    e.stopPropagation();
    var ip = $(this).parent().parent().find('.ipAddress').text();
    unregisterStation(ipAddress);
  })
}

function unregisterItem(uuid) {
  $.ajax({
    'url': 'unregisterItem',
    'type': 'POST',
    'success': function(data) {},
    'error': function() {
      console.error("Error: can't unregister");
    }
  });
}

function unregisterStation(ipAddress) {
  $.ajax({
    'url': 'unregisterStation',
    'type': 'POST',
    'success': function(data) {},
    'error': function() {
      console.error("Error: can't unregister");
    }
  });
}