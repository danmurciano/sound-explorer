### Getting Started
Create a fresh virtual env and install the dependencies from the requirements.txt file:
```bash
pip install -r requirements.txt
```
Run the development server:
```bash
flask run
```
Open [http://localhost:5000](http://localhost:5000) with your browser to see the result.


Deployed app - [https://sound-explorer.herokuapp.com/](https://sound-explorer.herokuapp.com/)

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### Description
Sound Explorer is a Flask based web app that is powered by the Spotify API. It allows users to get music recommendations based off a reference track they provide, and turn these into Spotify playlists. The app employs AJAX practices, where user actions in the front end are handled by JavaScript. User initiated API requests are sent from the front end to the appropriate backend routes and are handled there, returning data to the front end if needed.


### User Interface
The app has a basic mode and a registered user mode. The registered user mode requires a Spotify account.
On the basic mode, the app initially loads with an autocomplete search field, where the user can type names of tracks and artists. Every change to the input (so long it is at least 2 characters long) sends a request to the Spotify API and updates the autocomplete results. The user can then select an option to be committed to the field. The user can also select the desired level of popularity and the desired number of results via dedicated select boxes. The user can then click the submit button, which sends a request to the Spotify API, that returns recommended tracks and display them on the page. Tracks that have a preview available by Spotify (not all tracks do), will have a play button next to them, that will trigger a 30 seconds audio preview.

The registered user mode allows for some added functionality. After getting recommendations, the user can turn them into a playlist, that will be saved into his Spotify account. Also, he can access an account page, where all of his existing playlists are displayed. Clicking a playlist will open it in the Spotify player on a new tab.


### Backend Logic
Spotify provides various audio features for every track based on an audio analysis algorithm. However, through some experimentation it was concluded that most of these are far from being reliable or to provide any significant insight regarding the music. The one exception was “Energy”, that seemed closely correlated with what was expected. Therefore, “Energy” score for the reference track has been added to the request, in order to dial in the recommendations more accurately.

When a recommendations request is triggered by the user:
1. A request is made to retrieve audio features for the reference track.
2. A second request is made to get audio recommendations based on the reference track, the desired level of popularity, the      desired number of results and the Energy score retrieved in step 1.
3. After getting a response, the recommended tracks are displayed on the page.

A special case is handled when a user selects the “Obscure” option in the Popularity box. This option can be useful for music supervisors or directors looking for music that might be cheaper to obtain, but still have something in common with their reference track. This special case requires diving a little deeper in order to get meaningful results. Therefore, after the initial request is made, the results are sorted by popularity. Subsequent requests are then made with the 4 list popular tracks, and the result of all 5 requests are again sorted by popularity (after removing duplicates). The 20, 50 or 100 list popular tracks (based on user’s selection) are then returned as the results. The number of 4 subsequent requests was chosen as a reasonable compromise between thoroughness and speed.


### Authentication
On the basic mode, the app is authenticated to the Spotify API with client credentials. That allows the app to interact with Spotify.
When a user clicks the “Connect Spotify” button a Spotify user authentication is triggered. If the user has been successfully authenticated, a token will be provided by Spotify, and will be stored in the app’s session. The app will also try to look for the user in its database (PostgreSQL is used). If found, the user will be stored in the app’s session. Otherwise, a new user with the data retrieved from Spotify will be created and committed to the database.
