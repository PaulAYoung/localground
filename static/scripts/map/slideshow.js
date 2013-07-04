localground.slideshow = function(){
    this.player = null;
    this.id = 'slideshow-carousel';
    this.height = '360px';
    this.width = '480px';
};

localground.slideshow.prototype.initialize=function(opts){
    if(opts){ $.extend(this, opts); }
    this.player = new localground.player({mode: 'small'});
    this.player.initialize(opts);
    if(opts.renderFlashPlayer)
        $('body').append(this.player.renderFlashObject(opts));
};

localground.slideshow.prototype.generateCarousel = function() {
    return $('<div />').addClass('carousel slide').attr('id', this.id)
        .append(
            $('<div />').addClass('carousel-inner'))
        .append(
            $('<a />').addClass('left carousel-control')
                .attr('href', '#' + this.id)
                .attr('data-slide', 'prev').html('&lsaquo;'))
        .append(
            $('<a />').addClass('right carousel-control')
                .attr('href', '#' + this.id)
                .attr('data-slide', 'next').html('&rsaquo;')
        );
};

            
localground.slideshow.prototype.render_slideshow = function(opts) {
    var marker = opts.marker, $container = opts.$container;
    $container.append(this.generateCarousel());
    this.render_title_page(marker);
    this.render_photo_slides(marker);
    //this.render_data_slides(marker);
    this.render_audio(marker);
    var $c = $('#' + this.id).carousel('pause');
    if(opts.applyHack) {
        $('.left, .right').click('[data-slide]', function(e){
            var $this = $(this), href
            , $target = $c, options = $.extend({}, $target.data(), $this.data())
          $target.carousel(options)
          e.preventDefault()  
        });
    }
}

localground.slideshow.prototype.render_title_page = function(marker) {
    var $page = $('<div />');
    $page.append($('<h1 />')
                    .css({margin: '5px 0px 10px 5px'})
                    .append($('<img />')
                            .addClass('header-icon')
                            .attr('src', '/static/images/place_marker_large.png'))
                    .append(marker.name));
    var $body = $('<div />')
                    .css({'margin': '0px 0px 0px 70px', color: '#444'})
                    .append(marker.description);
    if (marker.photos && marker.photos.data.length > 0) {
        var $holder = $('<div />')
                            .css({
                                'display': 'block',
                                'margin-left': 'auto',
                                'margin-right': 'auto'
                                /*,
                                'border': 'solid 1px #000'*/
                            });
        $.each(marker.photos.data, function(idx) {
            if (idx < 2) { 
                $holder.append($('<img />').addClass('thumb')
                             .css({ height: '90px', 'margin-right': '3px' })
                             .attr('src', this.path_small));
            }
        });
        $body.append($holder);
    }
    $page.append($body);
    var $item = $('<div />').addClass('item active')
            .append($('<div />').css({
                height: this.height,
                width: this.width,
                color: '#fff',
                display: 'block'
            }).append($page))
            .append($('<div />').addClass('carousel-caption')
                .append($('<h4 />').html(marker.name)
                .append($('<p />').html(marker.description || 'Description!'))
            ));
    $('#' + this.id).find('.carousel-inner').append($item);
};

            
localground.slideshow.prototype.render_photo_slides = function(marker) {
    var me = this;
    $.each(marker.photos.data, function(idx) {
        var $item = $('<div />').addClass('item')
                .append($('<div />').css({'height': me.height})
                        .append(
                            $('<img />')
                                .attr('src', this.path_large)
                                .css({
                                    'max-height': me.height,
                                    'display': 'block',
                                    'margin-left': 'auto',
                                    'margin-right': 'auto'
                                })
                        )
                )
                .append(
                    $('<div />').addClass('carousel-caption')
                        .append($('<h4 />').html(this.name || 'Untitled Photo'))
                        .append($('<p />').html(this.caption || 'No caption available.'))
                );
        //if(idx == 0) { $item.addClass('active'); }
        $('#' + me.id).find('.carousel-inner').append($item);
    });
};

localground.slideshow.prototype.render_audio = function(marker) {
    var me = this;
    if(marker.audio == null || marker.audio.data.length == 0){
        return;
    }
    var playerHtml = this.player.renderPlayerObject();
    $('#' + this.id).append(
        $('<div />').addClass('audio-controller')
            .append(playerHtml)
    );
    $.each(marker.audio.data, function(idx) {
        if(idx > 0)
            playerHtml.append($('<input type="hidden" />').val(this.file_path));    
        else
            playerHtml.find('input').val(this.file_path);
    });
    this.player.initialize();
};

localground.slideshow.prototype.render_data_slides = function(marker) {
    var me = this;
    $.each(marker.tables, function(idx) {
        var tableName = this.name;
        $.each(this.data, function(){
            var $data = $('<div />').css({'padding': '20px 0px 0px 70px'});
            this.noMap = true;
            var record = new localground.record(this, null, this.id);
            $data.append(record.renderSlideRecord());
            var $item = $('<div />').addClass('item')
                    .append($('<div />').css({
                        height: me.height,
                        width: me.width,
                        color: '#fff',
                        display: 'block'
                    }).append($data))
                    .append($('<div />').addClass('carousel-caption')
                        .append($('<h4 />').html(tableName)
                        .append($('<p />').html('&nbsp;'))
                    ));
            $('#' + me.id).find('.carousel-inner').append($item);
        });
    });
};


            
localground.slideshow.prototype.get_photos_by_marker_id = function(id) {
    var me = this;
    var url = '/api/0/get/marker/' + id + '/';
    $.getJSON(url, {},
        function(result) {
            if(!result.success) {
                alert(result.message);
                return;
            }
            me.render_slides(result.obj);
            me.render_audio(result.obj);
            $('#slide-modal').modal();    
        },
    'json');   
};
            
localground.slideshow.prototype.get_photos_by_project_id = function(id) {
    var me = this;
    var params = {
        include_processed_maps: true,
        include_markers: true,
        include_audio: true,
        include_photos: true
    };
    var url = '/api/0/projects/' + 97 + '/';
    $.getJSON(url, params,
        function(result) {
            if(!result.success) {
                alert(result.message);
                return;
            }
            $.each(result.data, function() {
                if(this.id == 'photo') {
                    me.render_photos(this.data);
                    me.render_audio([]);
                }
            });
        },
    'json');   
};