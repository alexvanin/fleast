# fleast
Least-favourite twitch streamers here


## Change Log
### 1.10.0
#### Changed
- Refresh website design

### 1.9.1
#### Fixed
- Server does not fail when processing API response withour `cursor` field.
- String formatting for older python3 versions.

### 1.9
#### Fixed
- Char escaping and various typos.
- Unique filter for streams.

#### Added
- Runtime ouath token generation.

#### Changed
- Use threshold on amount of returned streams to resend requests.

#### Removed
- v5 (kraken) API support.
- Daemonizer component.

### 1.8
#### Fixed
- Search queries for v5 and v6 API

### 1.7
- Fixed bug with displaying special symbols in stream name
### 1.6
- Fixed bug, when IRL query could contain several copies of one stream
### 1.5
- IRL section is back with IRL query
- Fixed bug when games with `&` symbol could not found correctly.  
### 1.4
- Polished internal code and now cherrypy server configuration 
is independent from nginx reverse proxy
### 1.3
- Fixed bug when VOD-streams appear in list of live streams
### 1.2
- Fixed some typos in text
- Fixed bug with chinese language streams
- Fixed bug when 0 streams are found if game name contains whitespaces in the end
- Fixed bug with stream list if stream name contains '<' and '>' symbols
### 1.1
- Form data now saved between querries
### 1.0
- Initial release
