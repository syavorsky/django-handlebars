
(function(hb, jQuery){

    if(!window.handlebars_config){ throw new Error('No handlebars_config'); }
    if(!hb){ throw new Error('No Handlebars object'); }
    
    var cnf = window.handlebars_config,
        compiled = cnf.loadurl.match(/\.js$/),
        isfunc = function(value){ return typeof value === 'function'; },
        isundef = function(value){ return typeof value === 'undefined'; },
        isstr = function(value){ return typeof value === 'string'; },
        tplurl = function(name){ return cnf.loadurl.replace('{tpl}', name); },
        evaltpl = function(tpl){ return compiled ? eval('(' + tpl + ')') : tpl; },
        noop = function(){},
        load = null,
        defer = null;
    
    if(isfunc(cnf.load)){
        
        load = cnf.load;
        
    }else if(jQuery){
	    
        load = function(url, cache, error){
            var promise = jQuery.Deferred().fail(error);
                
	        jQuery.ajax(url, {dataType: 'text'})
            .done(function(tpl){
                promise.resolve(cache(tpl)); 
            })
            .fail(function(xhr, err){
                promise.reject(xhr, err); 
            });
            
            return promise;
	    };
        
        defer = function(func){ 
            return function(){
	            var promise = jQuery.Deferred().done(func);
	            return promise.resolve.apply(promise, arguments);
	        }
        };

    }else{
    
		var getxhr = null,
            xhr_factories = [
			    function(){ return new XMLHttpRequest(); },
			    function(){ return new ActiveXObject("Msxml2.XMLHTTP"); },
			    function(){ return new ActiveXObject("Msxml3.XMLHTTP"); },
			    function(){ return new ActiveXObject("Microsoft.XMLHTTP"); }
			];
		
	    while(!getxhr && xhr_factories.length){
            getxhr = xhr_factories.shift();
            try { getxhr(); }catch(e){ getxhr = null; }
        }
        
        if(!getxhr){ throw new Error('Your browser is not capable of AJAX functionality'); }
         
        load = function(url, success, error) {
            var xhr = getxhr();
            if (!xhr){ return; }
            
            xhr.open("GET", url, true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState != 4){ return; }
                if (xhr.status != 200 && xhr.status != 304) {
                    error(xhr, xhr.statusText);
                }else{
                    success(xhr.responseText);
                }
            };
            xhr.send();
        };

    }

    hb.templates = hb.templates || {};

    hb.tpl = function(name, tpl){
        name = name.replace(/^\/|\/$/, '');
        tpl = tpl || {};

        if(isfunc(tpl)) {
            this.templates[name] = this.template(tpl);
            return this.templates[name];
            
        } else if(isstr(tpl)) {
            this.templates[name] = this.compile(tpl);
            return this.templates[name];
            
        }
        
        var success = isfunc(tpl.success) ? tpl.success : noop;
        
        if(isundef(this.templates[name])) {
            var cache = function(t){ 
                    t = hb.tpl(name, evaltpl(t))
                    success(t);
                    return t; 
                }, 
                error = isfunc(tpl.error) ? tpl.error : noop;
                
            return load(tplurl(name), cache, error);
        }
        
        return defer ? defer(success)(this.templates[name]) : success(this.templates[name]);
    };
    
}(window.Handlebars, window.jQuery || (window.django && window.django.jQuery)));
