const BASE_URL = "http://localhost:5000";

$("#search-results").hide();
$("#selected-track").hide();
$("#loading").hide();
$("#playlist").hide();
$(".save-btn").hide();
$(".modal-alert").hide();

let searchResults;
let selectedTrack;
let seedTrack;
let suggestedTracks;
let currentTrack;
let audio;


function createListItem(track) {
  return `
  <div class="results-item list-item" id=${track.id}>
    <img src=${track.album.images[2].url} alt="...">
      ${track.name} - ${track.artists[0].name} &nbsp ${track.album.release_date.slice(0,4)}
  </div>
  `;
}


function createTableItem(track) {
  if (track.preview_url) {
    return `
      <tr class="playlist-item">
        <td>
          <i class="bi bi-play" data-url=${track.preview_url}></i>
        </td>
        <td>
          <img src=${track.album.images[2].url} alt="..." class="playlist-img">
        </td>
        <td>
          <p class="track-title"> ${track.name} </p>
          <p> ${track.artists[0].name} </p>
        </td>
        <td> ${track.album.name}</td>
        <td> ${track.album.release_date.slice(0,4)}</td>
        <td>
          <div class="progress">
            <div class="progress-bar" role="progressbar" style="width: ${track.popularity}%"/>
          </div>
        </td>
      </tr>
    `;
  } else {
    return `
      <tr class="playlist-item">
        <td> </td>
        <td>
          <img src=${track.album.images[2].url} alt="..." class="playlist-img">
        </td>
        <td>
          <p class="track-title"> ${track.name} </p>
          <p> ${track.artists[0].name} </p>
        </td>
        <td> ${track.album.name}</td>
        <td> ${track.album.release_date.slice(0,4)}</td>
        <td>
          <div class="progress">
            <div class="progress-bar" role="progressbar" style="width: ${track.popularity}%"/>
          </div>
        </td>
      </tr>
    `;
  }
}


function initializeSaveModal() {
  const shortTrackName = seedTrack.name.split(' ').slice(0, 4).join(' ');
  $("#plImage").attr("src", seedTrack.album.images[1].url);
  $("#plName").val("");
  $("#plDescription").val("");
  $(".modal-alert").hide();
}


// Search track autocomplete
$("#title").on("input", async function(evt) {
  evt.preventDefault();
  pauseAudio();
  if ($("#title").val().length >= 2) {
    let url = `${BASE_URL}/`;
    let q = $("#title").val();
    let payload = {q};
    const response = await axios.post(url, payload);
    searchResults = response.data.tracks;
    $("#search-results").empty();

    for (track in searchResults) {
      let newItem = $(createListItem(searchResults[track]));
      $("#search-results").append(newItem);
      $("#title").trigger("reset");
    }
    if (searchResults.length > 0 && !selectedTrack) {
      $("#search-results").show();
    } else {
      $("#search-results").hide();
    }
  }
});


// Select track from dropdown options
$("#search-results").click(function(evt) {
  selectedTrack = $(evt.target).closest(".results-item");
  selectedTrack.addClass("selected-track form-control").removeClass("list-item");
  seedTrack = searchResults[selectedTrack.index()]
  $("#title").val("");
  $("#selected-track").prepend(selectedTrack);
  $("#search-results").hide();
  $("#search-input").hide();
  $("#selected-track").show();
});


// Collapse dropdown when clicked outside of it
$(document).click(function(evt) {
  $("#search-results").hide();
});


// Remove selected track when x button is clicked
$("#selected-track > span").click(function(evt) {
  pauseAudio();
  $("#selected-track").hide();
  $("#selected-track > div").remove();
  $("#search-input").show();
  selectedTrack = undefined;
});


// Submit seed-form to get suggested tracks
$(".submit-btn").click(async function(evt) {
  if (selectedTrack) {
    pauseAudio();
    $(".save-btn").hide();
    $(".submit-btn").hide();
    $("#loading").show();
    let url = `${BASE_URL}/seed-playlist`;
    let id = $(".selected-track").attr("id");
    let popularity = $("#popularity").val();
    let limit = $("#limit").val();
    let payload = {id, popularity, limit};
    const response = await axios.post(url, payload);
    suggestedTracks = response.data.tracks;
    $("#playlist").hide();
    $("#playlist > table > tbody").empty();

    for (track in suggestedTracks) {
      let newItem = $(createTableItem(suggestedTracks[track]));
      $("#playlist > table > tbody").append(newItem);
    }
    $("#loading").hide();
    $(".submit-btn").show();
    if (suggestedTracks.length > 0) {
      $("#playlist").show();
      if (response.data.user) {
        $(".save-btn").show();
      }
    }

    initializeSaveModal();
  }
});


// play/pause preview audio
$("#playlist").click(function(evt) {
  const target = $(event.target);
  if (target.is("i")) {
    if (!currentTrack) {
      playAudio(target);
    } else if (currentTrack && currentTrack[0] === target.closest(".playlist-item i")[0]) {
      pauseAudio();
    } else if (currentTrack && currentTrack[0] !== target.closest(".playlist-item i")[0]) {
      pauseAudio();
      playAudio(target);
    }
  }
});

function playAudio(target) {
  audio = new Audio(target.attr("data-url"));
  audio.addEventListener("ended", function(evt) {
    currentTrack.toggleClass("bi-play bi-pause");
    currentTrack.closest("tr").toggleClass("playlist-item-active");
    currentTrack = undefined;
  });
  currentTrack = target.closest(".playlist-item i");
  currentTrack.toggleClass("bi-play bi-pause");
  target.closest("tr").toggleClass("playlist-item-active");
  audio.play();
}

function pauseAudio() {
  if (currentTrack) {
    currentTrack.toggleClass("bi-play bi-pause");
    currentTrack.closest("tr").toggleClass("playlist-item-active");
    currentTrack = undefined;
    audio.pause();
  }
}


// prevent line breaks in playlist description field
$("#plDescription").keypress(function (evt) {
    if (evt.keyCode === 13) {
      evt.preventDefault();
      $(".modal-alert").html(`<i class="bi bi-exclamation-circle"></i> Line breaks aren't supported in the description.`);
      $(".modal-alert").show();
    }
});


// Intitialize modal on hide
$("#save-modal").on("hidden.bs.modal", function() {
  initializeSaveModal();
});


// Pause audio when modal is opened
$(".save-btn").click(function() {
  pauseAudio();
});


// Save playlist
$(".modal-save").click(async function(evt) {
  if ($("#plName").val().length === 0) {
    $(".modal-alert").html(`<i class="bi bi-exclamation-circle"></i> Playlist name is required.`);
    $(".modal-alert").show();
  } else {
    let url = `${BASE_URL}/save-playlist`;
    let name = $("#plName").val();
    let description = $("#plDescription").val();
    let image = seedTrack.album.images[0].url;
    let payload = {name, description, image, suggestedTracks}

    const response = await axios.post(url, payload);
    if (response.status === 200) {
      document.location.href=`${BASE_URL}/users/${response.data}`;
    }
  }
});
