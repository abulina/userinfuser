# Copyright (C) 2011, CloudCaptive
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
""" All paths here run unit tests
"""

from google.appengine.api import mail, memcache
from google.appengine.ext import db, webapp
from google.appengine.ext.db import *
from serverside import constants
from serverside.entities import memcache_db
from serverside.entities.accounts import *
from serverside.entities.badges import *
from serverside.entities.pending_create import *
from serverside.entities.users import *
from serverside.entities.widgets import *
from serverside.session import Session
from serverside.tools.utils import account_login_required
from serverside.testing.dummydata import *
import cgi
import logging
import os
import time
import wsgiref.handlers

class TestDB(webapp.RequestHandler):
  def get(self):
   self.response.out.write("Test 1:" +self.test1() +"<br>")
   self.response.out.write("Test 2:" + self.test2() +"<br>")
   self.response.out.write("Test 3:" + self.test3() +"<br>")
   self.response.out.write("Test 4:" + self.test4() +"<br>")

  """ This test creates, updates, and deletes an Account """
  def test1(self):
    key = "test@test.com"
    ent_type = "Accounts"
    trophy_case_widget = TrophyCase(key_name=key)
    points_widget = Points(key_name=key)
    rank_widget = Rank(key_name=key)
    newacc = Accounts(key_name=key,
                     password="aaa",
                     email=key,
                     isEnabled="enabled",
                     accountType="bronze",
                     paymentType="free",
                     cookieKey="xxx",
                     apiKey="xxx",
                     trophyWidget=trophy_case_widget,
                     pointsWidget=points_widget,
                     rankWidget=rank_widget)
    try:
      memcache_db.delete_entity(newacc, key)
    except Exception:
      pass
    # Save and get saved ent
    ret = memcache_db.save_entity(newacc, key)
    sameent = memcache_db.get_entity(key, ent_type) 
    if sameent.email != key:
      return "Error getting same account. Subtest 1"

    # purge from memcache and get from db
    memcache.delete(key=key, namespace=ent_type)
    sameent = memcache_db.get_entity(key, ent_type)
    if sameent.email != key:
      return "Error getting same account from DB (no cache). Subtest 2"

    # Set and get new user name
    diction = {"email":"test2@test.com"}
    ret2 = memcache_db.update_fields(key, ent_type, diction)
    ret2 = sameent.put()
    if ret != ret2:
      self.response.out.write("Error getting key name")
    sameent = memcache_db.get_entity(key, ent_type)
    if sameent.email != "test2@test.com":
      return "Error getting same account after altering entity. Subtest 3"


    try:
      memcache_db.delete_entity(newacc, key)
    except Exception:
      return "Error deleting entity. Subtest 4"
      
    return "Success"

  """ This test creates, updates, and deletes a Badges entity"""
  def test2(self):
    account_key = "raj"
    trophy_case_widget = TrophyCase(key_name=account_key)
    points_widget = Points(key_name=account_key)
    rank_widget = Rank(key_name=account_key)
    newacc = Accounts(key_name=account_key,
                     password="aaa",
                     email="a@a.a",
                     isEnabled="enabled",
                     accountType="bronze",
                     paymentType="free",
                     apiKey="xxx",
                     cookieKey="xxx",
                     trophyWidget=trophy_case_widget,
                     pointsWidget=points_widget,
                     rankWidget=rank_widget)
    try:
      memcache_db.delete_entity(newacc, key)
    except Exception:
      pass

    # Save and get saved ent
    ret = memcache_db.save_entity(newacc, account_key)

    key = "testbadge1"
    ent_type = "Badges"
    newacc = Badges(key_name=key, 
                    name="badge1",
                    description=key,
                    altText="a really cool badge", 
                    setType="free",
                    isEnabled="yes",
                    creator=newacc,
                    permissions="private",
                    blobKey="xxxx",
                    storageType="blob") 
    try:
      memcache_db.delete_entity(newacc, key)
    except Exception:
      pass
    # Save and get saved ent
    ret = memcache_db.save_entity(newacc, key)
    sameent = memcache_db.get_entity(key, ent_type)
    if sameent.description != key:
      return "Error getting same account. Subtest 1"

    # purge from memcache and get from db
    memcache.delete(key=key, namespace=ent_type)
    sameent = memcache_db.get_entity(key, ent_type)
    if sameent.description != key:
      return "Error getting same account from DB (no cache). Subtest 2"

    # Set and get new user name
    diction = {"isEnabled":"no", "permissions":"public"}
    ret2 = memcache_db.update_fields(key, ent_type, diction)
    ret2 = sameent.put()
    if ret != ret2:
      self.response.out.write("Error getting key name")
    sameent = memcache_db.get_entity(key, ent_type)
    if sameent.isEnabled != "no" or sameent.permissions != "public":
      return "Error getting same account after altering entity. Subtest 3"

    try:
      memcache_db.delete_entity(sameent, key)
    except Exception:
      return "Error deleting entity. Subtest 4"

    try:
      memcache_db.delete_entity(newacc, account_key)
    except Exception:
      return "Error deleting account. Subtest 5"

    return "Success"

  """ This test creates, updates, and deletes User"""
  def test3(self):
    account_key = "a@a.a"
    trophy_case_widget = TrophyCase(key_name=account_key)
    points_widget = Points(key_name=account_key)
    rank_widget = Rank(key_name=account_key)
    newacc = Accounts(key_name=account_key,
                     password="aaa",
                     email="a@a.a",
                     isEnabled="enabled",
                     accountType="bronze",
                     paymentType="free",
                     apiKey="xxx",
                     cookieKey="xxx",
                     trophyWidget=trophy_case_widget,
                     pointsWidget=points_widget,
                     rankWidget=rank_widget)
    try:
      memcache_db.delete_entity(newacc, account_key)
    except Exception:
      pass

    # Save and get saved ent
    ret = memcache_db.save_entity(newacc, account_key)

    key = "testuser1"
    ent_type = "Users"
    newacc = Users(key_name=key,
                   userid=key,
                   isEnabled="yes",
                   accountRef=newacc,
                   tags = key)
    try:
      memcache_db.delete_entity(newacc, key)
    except Exception:
      pass
    # Save and get saved ent
    ret = memcache_db.save_entity(newacc, key)
    sameent = memcache_db.get_entity(key, ent_type)
    if sameent.tags != key:
      return "Error getting same entity. Subtest 1"

    # purge from memcache and get from db
    memcache.delete(key=key, namespace=ent_type)
    sameent = memcache_db.get_entity(key, ent_type)
    if sameent.tags != key:
      return "Error getting same entity from DB (no cache). Subtest 2"

    # Set and get new user name
    diction = {"tags":"goodbye:hello"}
    ret2 = memcache_db.update_fields(key, ent_type, diction)
    ret2 = sameent.put()
    if ret != ret2:
      self.response.out.write("Error getting key name")
    sameent = memcache_db.get_entity(key, ent_type)
    if sameent.tags != "goodbye:hello":
      return "Error getting same entity after altering entity. Subtest 3"


    try:
      memcache_db.delete_entity(newacc, account_key)
      memcache_db.delete_entity(sameent, key)
    except Exception:
      return "Error deleting entity. Subtest 4"
      
    return "Success"


  """ This test creates, updates, and deletes a BadgeInstance """
  def test4(self):
    account_key = "a@a.a"
    trophy_case_widget = TrophyCase(key_name=account_key)
    points_widget = Points(key_name=account_key)
    rank_widget = Rank(key_name=account_key)
    newacc = Accounts(key_name=account_key,
                     password="aaa",
                     email="a@a.a",
                     isEnabled="enabled",
                     accountType="bronze",
                     paymentType="free",
                     apiKey="xxx",
                     cookieKey="xxx",
                     trophyWidget=trophy_case_widget,
                     pointsWidget=points_widget, 
                     rankWidget=rank_widget)
    try:
      memcache_db.delete_entity(newacc, key)
    except Exception:
      pass

    # Save an account
    ret = memcache_db.save_entity(newacc, account_key)

    user_key = "testuser1"
    newuser = Users(key_name=user_key,
                   userid=user_key,
                   isEnabled="yes",
                   accountRef=newacc,
                   tags = user_key)
    try:
      memcache_db.delete_entity(newacc, user_key)
    except Exception:
      pass
    # Save a user
    ret = memcache_db.save_entity(newacc, user_key)

    # Create a Badge Type
    badge_key = "testbadge1"
    badgetype = Badges(key_name=badge_key,
                    name="badge1",
                    description=badge_key,
                    altText="a really cool badge", 
                    setType="free",
                    isEnabled="yes",
                    creator=newacc,
                    permissions="private",
                    storageType="blob",
                    blobKey="xxxx") 
    try:
      memcache_db.delete_entity(badgetype, badge_key)
    except Exception:
      pass
    # Save and get saved ent
    ret = memcache_db.save_entity(badgetype, badge_key)
 
    key = "testbadgeinstance1"
    ent_type = "BadgeInstance"
    badgeinstance = BadgeInstance(key_name=key,
                    awarded="no",
                    badgeRef=badgetype,
                    userRef=newuser,
                    pointRequired=10,
                    pointsEarned=0,
                    permissions="private") 
    try:
      memcache_db.delete_entity(badgeinstance, key)
    except Exception:
      pass
    # Save and get saved ent
    ret = memcache_db.save_entity(badgeinstance, key)
    sameent = memcache_db.get_entity(key, ent_type)
    if sameent.awarded != "no":
      return "Error getting same entity. Subtest 1"

    # purge from memcache and get from db
    memcache.delete(key=key, namespace=ent_type)
    sameent = memcache_db.get_entity(key, ent_type)
    if sameent.awarded != "no":
      return "Error getting same entity from DB (no cache). Subtest 2"

    # Set and get new user name
    diction = {"pointsRequired":11, "awarded":"no"}
    inc_diction = {"pointsEarned":5}
    ret2 = memcache_db.update_fields(key, ent_type, diction, inc_diction)
    ret2 = sameent.put()
    if ret != ret2:
      self.response.out.write("Error getting key name")
    sameent = memcache_db.get_entity(key, ent_type)
    if sameent.pointsRequired!= 11 \
          or sameent.pointsEarned != 5:
      return "Error getting same entity after altering entity. Subtest 3"


    # Cleanup
    try:
      memcache_db.delete_entity(badgeinstance, key)
    except Exception:
      return "Error deleting entity. Subtest 4"
    try:
      memcache_db.delete_entity(newacc, account_key)
    except Exception:
      return "Error deleting entity. Subtest 4"
    try:
      memcache_db.delete_entity(badgetype, badge_key)
    except Exception:
      return "Error deleting entity. Subtest 4"
    try:
      memcache_db.delete_entity(newuser, user_key)
    except Exception:
      return "Error deleting entity. Subtest 4"
       
    return "Success"

class TestPendingCreates(webapp.RequestHandler):
  def get(self):
    """ Add to the db, get, and delete """
    
    id = "91658085309165808530"
    email = "shanrandhawa@gmail.com"
    
    pending_create = Pending_Create(key_name=id, id=id, email=email)
    key = pending_create.put()
    
    
    self.response.out.write("Wrote (put) entity. They returned key = " + str(key) + "<br/>")
    
    ret = Pending_Create.get_by_key_name(id)
    if ret == None:
      self.response.out.write("Not found in DB<br/>")
    else:
      self.response.out.write("Entity returned: email: " + ret.email + ", id: " + ret.id + "<br/>")
      self.response.out.write("Attempt to delete it...<br/>")
      
      try:
        ret.delete()
      except NotSavedError:
        self.response.out.write("The entity that u are trying to delte was not in the datastore<br/>")
        return
      self.response.out.write("Seems like the entity was deleted successfully...<br/>")
      
      self.response.out.write("Try to look it up again...<br/>")
      ret = Pending_Create.get_by_key_name(id)
      if ret == None:
        self.response.out.write("Nothing found... that's good.")
      else:
        self.response.out.write("Something found... not good.")
    
 
class TestEncryption(webapp.RequestHandler):
  """Test encyption methods """
  def get(self):
    from serverside.tools import encryption
    """Do some simple encryption and show results """
    mystr = "hello, world"
    self.response.out.write("encrypt string: " + mystr + "<br/>")
    mystr_enc = encryption.des_encrypt_str("hello, world")
    self.response.out.write("encrypted: " + mystr_enc + "<br/>")
    mystr_dec = encryption.des_decrypt_str(mystr_enc)
    self.response.out.write("decrypted: " + mystr_dec + "<br/>")

    
class TestOSEnvironment(webapp.RequestHandler):
  """Test method to see how environments are defined"""
  
  def get(self):
    print "OS: " + os.environ["SERVER_SOFTWARE"]
    self.response.out.write("OS server software: " + os.environ["SERVER_SOFTWARE"])
    
    """Try constants"""
    self.response.out.write("<br/>CONSTANT: " + constants.WEB_SIGNUP_URLS.POST_DATA)
    
  
  def post(self):
    pass   
class TestCreateSession(webapp.RequestHandler):
  def get(self):
    self.response.out.write("Creating session and setting cookie")
    
    import uuid
    import time
    created_session = Session().create_session(self, "shanrandhawa@gmail.com", str(uuid.uuid4()), str(time.time() + WEB_ADMIN_PARAMS.VALID_FOR_SECONDS))
    if created_session == None:
      self.response.out.write("<br/>No session created")
    else:
      self.response.out.write("<br/>Session was created")
    
class TestViewLoggedIn(webapp.RequestHandler):
  @account_login_required
  def get(self):
    self.response.out.write("<br/>If you reached here you are logged in!")
    
    sess = Session().get_current_session(self)
    if(sess == None):
      self.response.out.write("<br/>You are not logged in!!")
    else:
      self.response.out.write("<br/>You are logged in as:")
      email = sess.get_email()
      self.response.out.write("<br/>" + email)

class TestTerminateSession(webapp.RequestHandler):
  def get(self):
    self.response.out.write("terminating the follow session:")
    sess = Session().get_current_session(self)
    if(sess == None):
      self.response.out.write("<br/>You are not logged in!!")
    else:
      self.response.out.write("<br/>You are logged in as:")
      email = sess.get_email()
      self.response.out.write("<br/>" + email)
      sess.terminate()

class TestViewLoggedOut(webapp.RequestHandler):
  def get(self):
    self.response.out.write("You should be able to see this page, logged in or not...")
    sess = Session().get_current_session(self)
    if(sess == None):
      self.response.out.write("<br/>You are not logged in!!")
    else:
      self.response.out.write("<br/>You are logged in as:")
      email = sess.get_email()
      self.response.out.write("<br/>" + email)
  
class TestAccount(webapp.RequestHandler):
  def get(self):
    pass

class TestBadges(webapp.RequestHandler):
  def get(self):
    pass

class TestUsers(webapp.RequestHandler):
  def get(self):
    pass

application = webapp.WSGIApplication([
  ('/test/db', TestDB),
  ('/test/accounts', TestAccount),
  ('/test/badges', TestBadges),
  ('/test/users', TestUsers),
  ('/test/encryption', TestEncryption),
  ('/test/environ', TestOSEnvironment),
  ('/test/createsession', TestCreateSession),
  ('/test/viewloggedin', TestViewLoggedIn),
  ('/test/terminatesession', TestTerminateSession),
  ('/test/viewloggedout', TestViewLoggedOut),
  ('/test/createdummyaccountsandusers', CreateDummyAccountsAndUsers),
  ('/test/createbatches', CreateDummyBatchData),
  ('/test/pendingcreates', TestPendingCreates)
], debug=True)


def main():
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
