'''
main handler and route definition
'''

# python
import logging
logging.basicConfig(level=logging.DEBUG)

# GAE
import webapp2

class MainHandler(webapp2.RequestHandler):
    
    def propfind(self, path):
        # allow propfind requests so we don't have to specify a server path when setting up WebDAV clients
        logging.critical('Redirecting from propfind path='+str(path))
        return self.redirect('/sync')

    def get(self, path):
        self.response.headers['Content-Type'] = 'text/plain'
        
        path = path.strip('/')

        if path.startswith('collections'): 
            import radicale.storage.appengine
            
            if path=='collections/create':
                #return self.response.write("(disabled)")
                
                radicale.storage.appengine.Collection('test').create()
                radicale.storage.appengine.Collection('test/contacts.vcf').create()
                radicale.storage.appengine.Collection('test/events.ics').create()

                return self.response.write("collections have been created ")

            if path=='collections/delete':
                #return self.response.write("(disabled)")
            
                radicale.storage.appengine.Collection('test/contacts.vcf').delete()
                radicale.storage.appengine.Collection('test/contacts.vcf').delete_items()
                radicale.storage.appengine.Collection('test/events.ics').delete()
                radicale.storage.appengine.Collection('test/events.ics').delete_items()
                radicale.storage.appengine.Collection('test').delete()
                
                return self.response.write("collections have been deleted ")

            if path=='collections/list':
                
                out = []
                
                for collection_container in radicale.storage.appengine.CollectionContainerClass.query():                    
                    out.append( '* COLLECTION: key=%s' % (', '.join([str(pair) for pair in collection_container.key.pairs()])) )
                    for bin, content in collection_container.debug_key_value():
                        out.append( '%s=%s' %(bin, str(content) ) )
                    out.append( '\n\n' )
 
                for item_container in radicale.storage.appengine.ItemContainerClass.query():                    
                    
                    out.append( '* item: key=%s' % (', '.join([str(pair) for pair in item_container.key.pairs()]) ) )
                    for key, value in item_container.debug_key_value():
                        out.append( '%s=%s' %(key, str(value) ) )
            
                    out.append( '\n\n' )
                
                return self.response.write('\n'.join(out))

        return self.response.write("You have requested:\n\n%s\n\nWe could serve any page we like here... Go to /collections/list for an image of the datastore."%path)

# monkey patching webapp2 to handle exotic methods (to allow for redirects to the correct handler)
for extra_method in ['PROPFIND']:
    if not extra_method in webapp2.WSGIApplication.allowed_methods:
        webapp2.WSGIApplication.allowed_methods = set( tuple(webapp2.WSGIApplication.allowed_methods) + (extra_method,) )
    
WSGI = webapp2.WSGIApplication([webapp2.Route(r'<path:.*>', handler=MainHandler)],
                               debug=True)

import radicale
WSGI_Radicale = radicale.Application()
radicale.log.start() # do not forget to start the logs