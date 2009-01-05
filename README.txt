This product makes is easy to send files by e-mail on top of a CPS portal

Dependencies: CPSSubscriptions

HOW TO INSTALL
--------------

Import CPSFileMailer 'default' profile and you're set

OPERATION
---------
It replaces the standard "notify_by_email" action so that
the created link serves the file directly with a token argument,
and no actual login. 

Since there's no other security than the token, you have to teach your users 
the obvious *confidentiality* issues.

The token lifetime can be specified in the portal_filemailer tool properties.
There's also an option to use a different base url in the link than the one used by
the current user.

The link provides the same revision that the user would see by navigation to the
document with his language settings

BEHIND THE SCENES
-----------------

A directory (filetokens) is used to keep the relation between 
doc id, token, expiration date. 

The default profiles installs a ZODB directory, but you're free to replace it 
with another kind (provided that DateTime objects are correctly supported)

You should regularly purge outdated tokens, which can be done by a simple GET on 
<portal_url>/portal_filemailer/purgeOutdatedTokens (Manager auth required). Don't 
forget to add ?__disable_cookie_login=1 if you want to perform a BASIC 
authentication (convenient with tools such as wget). 




