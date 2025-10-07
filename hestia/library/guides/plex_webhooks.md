Webhooks
Tip!: Webhooks are a premium feature and require an active Plex Pass subscription for admin/owner account of the Plex Media Server.

Introduction
Webhooks are a Plex Pass feature which allow you to configure one or more URLs to be hit by the Plex Media Server when certain things happen. You can use webhooks for any number of purposes: home automation (such as dimming lights when you start playback), posting to Slack or Twitter, or many other things. The webhooks can be consumed by a custom HTTP server, or a service like Zapier. Generally speaking, webhooks are a fairly advanced feature and won’t commonly be used by an “average” user.

Webhooks are configured under Account settings in Plex Web App (the Account item under the top right user menu), and are tied to a specific user. Servers receive webhooks for the user who is signed into the server, as well as webhooks for shared users. In this way, your webhooks “travel” with you, so regardless of the server you’re playing content from (as long as it’s running v1.3.4 or newer), the webhooks will be hit.

The webhooks are processed by posting a JSON payload to the configured URL. For some events, a small thumbnail JPEG is also included in a multipart message.



Webhook Events
There are several events which cause webhooks to be hit, along with the name of the events in the payload:

New Content
library.on.deck – A new item is added that appears in the user’s On Deck. A poster is also attached to this event.
library.new – A new item is added to a library to which the user has access. A poster is also attached to this event.
Playback
media.pause – Media playback pauses.
media.play – Media starts playing. An appropriate poster is attached.
media.rate – Media is rated. A poster is also attached to this event.
media.resume – Media playback resumes.
media.scrobble – Media is viewed (played past the 90% mark).
media.stop – Media playback stops.
Server Owner
These events are sent only for the server owner/admin account and relate to events on the server in general.

admin.database.backup – A database backup is completed successfully via Scheduled Tasks.
admin.database.corrupted – Corruption is detected in the server database.
device.new – A device accesses the owner’s server for any reason, which may come from background connection testing and doesn’t necessarily indicate active browsing or playback.
playback.started – Playback is started by a shared user for the server. A poster is also attached to this event.
Webhook Payload
The payload consists of five different parts.

Top-level: This contains event, user, and owner attributes. The event attribute holds the name of the event, as specified above. The user and owner flags indicate whether the event is sent because the user has a webhook configured (user flag is set) or because the server owner has a webhook set (the owner flag is set). This can be very useful for certain scenarios. Note that if a server owner triggers an event, both user and owner flags will be set.
Account: The account object contains information about the user who triggered the event, including ID, title, and in some cases, a URL for the user’s avatar image. Note that the owner ID will always be 1.
Server: The server object contains information about the server from which the event was generated, including the title and UUID.
Player: The player object contains information about the player which generated the event, if applicable. It contains the title of the player, its UUID, the public IP address of the player, and a local flag indicating whether or not it was on the same network as the server.
Metadata: This last object contains detailed information about the media.
With the details available in the payload, it’s possible for a webhook receiver to perform detailed filtering on the events. It may want to only look for events for a single player, or a single user, or all players local to the server, e.g.

As stated above, the payload is sent in JSON format inside a multipart HTTP POST request. For the media.play and media.rate events, a second part of the POST request contains a JPEG thumbnail for the media.

Example Payload
Here is an example payload:

{  
   "event": "media.play",
   "user": true,
   "owner": true,
   "Account": {
      "id": 1,
      "thumb": "https://plex.tv/users/1022b120ffbaa/avatar?c=1465525047",
      "title": "elan"
   },
   "Server": {
      "title": "Office",
      "uuid": "54664a3d8acc39983675640ec9ce00b70af9cc36"
   },
   "Player": {
      "local": true,
      "publicAddress": "200.200.200.200",
      "title": "Plex Web (Safari)",
      "uuid": "r6yfkdnfggbh2bdnvkffwbms"
   },
   "Metadata": {
      "librarySectionType": "artist",
      "ratingKey": "1936545",
      "key": "/library/metadata/1936545",
      "parentRatingKey": "1936544",
      "grandparentRatingKey": "1936543",
      "guid": "com.plexapp.agents.plexmusic://gracenote/track/7572499-91016293BE6BF7F1AB2F848F736E74E5/7572500-3CBAE310D4F3E66C285E104A1458B272?lang=en",
      "librarySectionID": 1224,
      "type": "track",
      "title": "Love The One You're With",
      "grandparentKey": "/library/metadata/1936543",
      "parentKey": "/library/metadata/1936544",
      "grandparentTitle": "Stephen Stills",
      "parentTitle": "Stephen Stills",
      "summary": "",
      "index": 1,
      "parentIndex": 1,
      "ratingCount": 6794,
      "thumb": "/library/metadata/1936544/thumb/1432897518",
      "art": "/library/metadata/1936543/art/1485951497",
      "parentThumb": "/library/metadata/1936544/thumb/1432897518",
      "grandparentThumb": "/library/metadata/1936543/thumb/1485951497",
      "grandparentArt": "/library/metadata/1936543/art/1485951497",
      "addedAt": 1000396126,
      "updatedAt": 1432897518
   }
}
Sample Code
We’ve made a few sample projects available so that you can see the sorts of things you can build using webhooks.

Notifications
A simple app which lets you control a Plex player using media keys, and displays native notifications during playback.



GitHub Repo: Notifications

Slack Integration
An app intended to be deployed on Heroku, which posts media scrobble and rating events into a Slack room.



GitHub Repo: Slack integration

Home Automation
A simple example of how to connect the webhooks up to recreate a theater lighting experience.

GitHub Repo: Home automation