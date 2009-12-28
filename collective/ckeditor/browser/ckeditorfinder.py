from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from collective.plonefinder.browser.finder import Finder



class CKFinder(Finder):
    """
    Custom Finder class for CKEditor
    """
    
    def __init__(self, context, request) :
        super(CKFinder, self).__init__(context, request)    
        self.findername = 'plone_ckfinder'
        self.multiselect = False 
        self.allowupload = True
        self.allowaddfolder = True
        context = aq_inner(context)                                              
        session = request.get('SESSION', None)    
        # store CKEditor function name in session for ajax calls
        session.set('CKEditorFuncNum', request.get('CKEditorFuncNum', ''))    
        # redefine some js methods (to select items ...)
        self.jsaddons = self.get_jsaddons()
        # set media type
        self.set_media_type()
        # store some properties in session (portal_type used for upload and folder creation ...)
        self.set_session_props()


    def set_media_type(self) :
        """
        set media type used for ckeditor
        """
        request = self.request                                       
        session = request.get('SESSION', None)
        self.media = session.get('media', request.get('media', 'file'))
    
    def set_session_props(self):
        """
        Take some properties from ckeditor to store in session
        """   
        request = self.request                                       
        session = request.get('SESSION', None)
        
        session.set('media', self.media)
        
        # typeupload
        self.typeupload = self.get_type_for_media(self.media)
        session.set('typeupload', self.typeupload)
        
        # typefolder
        self.typefolder = self.get_type_for_media('folder')
        session.set('typefolder', self.typefolder)        
            
        
    def get_type_for_media(self, media) :
        """
        return CKeditor settings for unik media_portal_type
        """
        context = aq_inner(self.context)
        request = self.request                                       
        session = request.get('SESSION', None)
        
        pprops = getToolByName(context, 'portal_properties')
        ckprops = pprops.ckeditor_properties
        
        prop = ckprops.getProperty('%s_portal_type' %media)
        
        if prop == 'auto' :
            return ''
        elif prop != 'custom' :
            return prop
        
        scopeType = self.scope.portal_type
        
        # custom type depending on scope
        mediatype = ''
        customprop = ckprops.getProperty('%s_portal_type_custom' %media)        
        for pair in customprop :
            listtypes = pair.split('|')
            if listtypes[0]=='*' :
                mediatype = listtypes[1]
            elif listtypes[0]== scopeType :    
                mediatype = listtypes[1]
                break
        return mediatype        
        

    def get_jsaddons(self) :
        """
        redefine selectItem method
        in js string
        """    
        context = aq_inner(self.context)
        request = aq_inner(self.request)                                       
        session = request.get('SESSION', None)
        CKEditor = session.get('CKEditor', '')
        CKEditorFuncNum = session.get('CKEditorFuncNum', '')
        
        jsstring = """
selectCKEditorItem = function (UID) {
	window.opener.CKEDITOR.tools.callFunction( %s, './resolveuid/' + UID );
	window.close();
};
Browser.selectItem = selectCKEditorItem;
             """ % CKEditorFuncNum
        
        return jsstring