const BASE_URL = "http://localhost:5000";

$("#search-results").hide();
$("#selected-track").hide();
$("#playlist").hide();

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


// Search track autocomplete
$("#title").on("input", async function(evt) {
  evt.preventDefault();
  if ($("#title").val().length >= 2) {
    let url = `${BASE_URL}/`;
    let q = $("#title").val();
    let payload = {q};
    const response = await axios.post(url, payload);
    let tracks = response.data.tracks;
    $("#search-results").empty();
    for (track in tracks) {
      let newItem = $(createListItem(tracks[track]));
      $("#search-results").append(newItem);
      $("#title").trigger("reset");
    }
    if (tracks.length > 0) {
      $("#search-results").show();
    } else {
      $("#search-results").hide();
    }
  }
});


// Select track from dropdown options
$("#search-results").click(function(evt) {
  let selectedTrack = $(evt.target).closest(".results-item");
  selectedTrack.addClass("selected-track form-control").removeClass("list-item");
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
  $("#selected-track").hide();
  $("#selected-track > div").remove();
  $("#search-input").show();
});


// Submit form to get results
// $("#seed-form").submit(async function(evt) {
$(".submit-btn").click(async function(evt) {
  let url = `${BASE_URL}/playlist`;
  let id = $(".selected-track").attr("id");
  let popularity = $("#popularity").val();
  let limit = $("#limit").val();
  let payload = {id, popularity, limit};
  const response = await axios.post(url, payload);
  let tracks = response.data.tracks;
  console.log(tracks);
  let trackNums = tracks.keys();
  $("#playlist > table > tbody").empty();

  for (const n of trackNums) {
    tracks[n].num = n + 1;
    let newItem = $(createTableItem(tracks[n]));
    $("#playlist > table > tbody").append(newItem);
  }
  if (tracks.length > 0) {
    $("#playlist").show();
  } else {
    $("#playlist").hide();
  }
});


let currentTrack = null;
let audio;

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
    currentTrack = null;
  });
  currentTrack = target.closest(".playlist-item i");
  currentTrack.toggleClass("bi-play bi-pause");
  target.closest("tr").toggleClass("playlist-item-active");
  audio.play();
}

function pauseAudio() {
  currentTrack.toggleClass("bi-play bi-pause");
  currentTrack.closest("tr").toggleClass("playlist-item-active");
  currentTrack = null;
  audio.pause();
}
