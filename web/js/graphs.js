$(function () {

    var AXIS = {
        'disk': 'percent',
        'network': 'percent',
        'cpu': 'percent',
        'max': 'percent',
        'mean': 'percent',
        'cu': 'cpu',
        'cs': 'cpu',
        'ci': 'cpu',
        'cn': 'cpu',
        'cw': 'cpu',
        'nr': 'network',
        'nw': 'network',
        'dr': 'disk',
        'dw': 'disk'
    };
    var MILLI_PER_SECOND = 1000;

        var PERC_AXIS = {'disk': true, 'network': true, 'cpu': true, 'max': true, 'mean': true};

    //globals
    var times;


    function getSeparateYaxis(series) {
        //var yAxis = [];
        //yAxis.push({min: 0, max: 1.2});
        var yAxis = [{
            min: 0,
            max: 1.5,
            opposite: false,
            formatter: function() { return this.value * 100 + ' %'; },
            id: 'percent',
            title: {text: 'PERC'}
        },
        {
            min: 0,
            max: 3200,
            opposite: false,
            id: 'cpu',
            title: {text: 'CPU'}
        },
        {
            min: 0,
            max: 150e6,
            opposite: false,
            id: 'disk',
            title: {text: 'D R/W'}
        },
        {
            min: 0,
            max: 100e6,
            opposite: false,
            id: 'network',
            title: {text: 'N R/W'}
        }];
        $.each(series, function(i, v) {
             if (v.name in AXIS) {
                 v.yAxis = AXIS[v.name];
             } else {
                 yAxis.push({labels: {enabled: false}, id: "" + i, title: {text: v.name}});
                 v.yAxis = "" + i;
             }
        });
        return yAxis;
    }
    /*
    function getSeparateYaxis(series) {
        var yAxis = [];
        yAxis.push({
            min: 0,
            max: 1.5,
            opposite: false,
            formatter: function() { return this.value * 100 + ' %'; },
            id: 'percent'
        });
        yAxis.push({
            min: 0,
            max: 3200,
            opposite: false,
            id: 'cpu'
        });
        yAxis.push({
            min: 0,
            max: 150e6,
            opposite: false,
            id: 'disk'
        });
        yAxis.push({
            min: 0,
            max: 100e6,
            opposite: false,
            id: 'network'
        });
        for (var i = 0; i < series.length; i++) {
            yAxis.push({
                labels: {
                    enabled: false
                },
                id: i
            });
            series[i].yAxis = (series[i].name in AXIS) ? AXIS[series[i].name] : i;
        }
        return yAxis;
    }
*/
    function dateToEpochTime(d) {
        if (typeof d === 'string') {
            d = new Date(d);
        }
        return Math.round(d.getTime() / 1000);
    }

    function genSeries(yperfText, start, end) {
        start = dateToEpochTime(start);
        end = dateToEpochTime(end);
        var lines = yperfText.split('\n');
        if (lines.length !== 3600) {
            console.warn('Yperf file unexpected length of: ' + lines.length + '.');
        }
        var series = [];
        var firstTime = true;
        var all_metrics = {'Max %': []};
        var cum_info = [{
                num: ['cu', 'cs'],
                den: 3200,
                name: 'CPU %'
            }, {
                num: ['nr', 'nw'],
                den: 550e6,
                name: 'Network %'
            }, {
                num: ['dr', 'dw'],
                den: 150e6,
                name: 'Disk %'
        }];
        var prevTime;
        for (var i = 0; i < lines.length; i++) {
            if (lines[i] === "") {
                if (i !== lines.length - 1) {
                    console.warn('Unexpected empty line.');
                }
                continue;
            }
            var vals = lines[i].split('\t');
            var time = parseInt(vals[0], 10);
            if (time < start) continue;
            if (time > end) break;
            if (firstTime) {
                if (time !== start) {
                    console.warn('Expected start time', start, 'got time', time);
                }
            } else {
                for (var null_ind = prevTime + 1; null_ind < time; null_ind++) {
                    console.warn('Missing value at time', null_ind, ',inserting null');
                    for (var metr_n in all_metrics) {
                        all_metrics[metr_n].push(null);
                    }
                }
            }
            var obj = JSON.parse(vals[1]);
            for (var name in obj) {
                if (!(name in all_metrics)) {
                    if (!firstTime) {
                        console.warn('New raw metric appeared later in file.');
                    }
                    all_metrics[name] = [];
                }
                var int_val = parseInt(obj[name], 10);
                all_metrics[name].push(int_val);
                obj[name] = int_val;
            }
            var max_perc = -1.0;
            for (var cum_ind = 0, len = cum_info.length; cum_ind < len; cum_ind++) {
                var info = cum_info[cum_ind];
                var sum = 0;
                for (var name_ind = 0, len2 = info.num.length; name_ind < len2; name_ind++) {
                    sum += obj[info.num[name_ind]];
                }
                if (firstTime) {
                    all_metrics[info.name] = [];
                }
                var perc = sum / info.den;
                all_metrics[info.name].push(perc);
                if (perc > max_perc) {
                    max_perc = perc;
                }
            }
            all_metrics['Max %'].push(max_perc);
            if (firstTime) {
                for (var metricName in all_metrics) {
                    series.push({
                        name: metricName,
                        data: all_metrics[metricName],
                        pointStart: start * MILLI_PER_SECOND,
                        pointInterval: MILLI_PER_SECOND,
                        visible: metricName in PERC_AXIS && metricName !== 'Max %'
                    });
                }
            }
            firstTime = false;
            prevTime = time;
        }
        return series;
    }

    function setSeriesDefaults(json_series, pointStart) {
        var VISIBLE = {'disk': true, 'network': true, 'cpu': true};
        for (var i = 0, len = json_series.length; i < len; i++) {
            var series = json_series[i];
            series.visible = series.name in VISIBLE;
            series.pointStart = pointStart;
        }
    }

    function renderGraph(json_response, name) {
        var series = json_response.series;
        pointStart = (json_response.epoch_start - times[0]) * MILLI_PER_SECOND;
        setSeriesDefaults(series, pointStart);
        var yAxis = getSeparateYaxis(series);
        var plotLines = [];
        for (var i = 0, i_lim = times.length; i < i_lim; i++) {
            var text;
            if (i == 0) text = 'Start'
            else if (i == 1) text = 'Servers Running'
            else text = 'ss' + (i - 1) + ' end.'
            plotLines.push({
	    		value: (times[i] - times[0]) * MILLI_PER_SECOND,
	    		width: 1,
	    		color: 'green',
	    		dashStyle: 'dash',
	    		label: {
	    			text: text,
	    			align: 'right',
	    			y: 12,
	    			x: 0
	    		}
	    	});
        }
        hc_div = $('<div>');
        $('#content')
          .find('#' + getId(name))
          .append(hc_div);
        hc_div
          .highcharts('StockChart', {
            legend: {
              enabled: true
            },
            title: {
              text: name.title
            },
            pointStart: pointStart,
            pointInterval: MILLI_PER_SECOND,
            yAxis: yAxis,
            series: series,
            xAxis: {
              min: 0,
              max: (times[times.length - 1] - times[0]) * MILLI_PER_SECOND,
              plotLines: plotLines
            }
          });
        $(window).trigger('resize');
    }

    function genGraphs(graphNames) { //TODO delete
        $.each(graphNames, function(i, name) {
            $.getJSON('json/' + name.file, function(data) {
                renderGraph(data, name);
            });
        });
    }

    function formatNumberLarg(o) {
        orig = o.aData[o.iDataColumn];
        num = parseFloat(orig);
        if (isNaN(num)) return orig;
        whole = Math.floor(num);
        res = o.oSettings.fnFormatNumber(whole);
        if (whole == num) return res;
        dec = num - whole;
        rounded = dec.toFixed(1);
        return res + rounded.substr(1);
    }

    function formatNumberWhole(o) {
        return o.oSettings.fnFormatNumber(Math.round(o.aData[o.iDataColumn]));
    }

    function formatNumberPerc(o) {
        orig = o.aData[o.iDataColumn];
        perc = orig * 100;
        return Math.round(perc);
    }

    function renderTable(data, name) {
        var div = $('#' + getId(name));
        var bigFormatter = div.attr('id').substr(0, 3) === 'avg' ? formatNumberLarg : formatNumberWhole;
        div.html('<table cellpadding="0" cellspacing="0" border="0" class="display"></table>');
        data.bFilter = false;
        data.bPaginate = false;
        data.order = [[ 0, 'asc' ]]
        for (var i = 0, len = data.aoColumns.length; i < len; i++) {
            title = data.aoColumns[i].sTitle;
            var formatter = null;
            if (title.length == 2) {
              formatter = bigFormatter;
            } else if (title == 'max' || title == 'mean' || title == 'cpu' || title == 'network' || title == 'disk') {
                formatter = formatNumberPerc;
            }
            if (formatter !== null) data.aoColumns[i].fnRender = formatter;
            data.aoColumns[i].sClass = 'right';
        }
        div.find('table').dataTable(data);
    }

    function getId(name) {
        return name.file.replace(/\./g, '');
    }

    function genAccordion(allNames) {
      accordion = $('<div>', {id: 'accordion'});
      $.each(allNames, function(k, name) {
        accordion
          .append([
            $('<h3>', {text: name.title})
                .data(name),
            $('<div>', {id: getId(name)})
          ])
      });
      $('#content')
        .append(accordion);
      accordion
          .addClass("ui-accordion ui-accordion-icons ui-widget ui-helper-reset")
          .find("h3")
          .addClass("ui-accordion-header ui-helper-reset ui-state-default ui-corner-top ui-corner-bottom")
          .hover(function() { $(this).toggleClass("ui-state-hover"); })
          .prepend('<span class="ui-icon ui-icon-triangle-1-e"></span>')
          .click(function() {
              var head = $(this);
              head
                  .find("> .ui-icon").toggleClass("ui-icon-triangle-1-e ui-icon-triangle-1-s").end()
                  .next().toggleClass("ui-accordion-content-active").slideToggle();
              if (!head.hasClass("loading-started")) {
                  head.addClass("loading-started");
                  var dat = head.data();
                  if (dat.type == 'table') {
                      $.getJSON('json/' + dat.file, function(data) {
                          renderTable(data, dat);
                          $(window).resize();
                      });
                  } else if (dat.type == 'graph') {
                      $.getJSON('json/' + dat.file, function(data) {
                          renderGraph(data, dat);
                          $(window).resize();
                      });
                  } else {
                      console.error('Type', dat.type, 'not recognized');
                  }
              }
              return false;
           })
      .next()
          .addClass("ui-accordion-content  ui-helper-reset ui-widget-content ui-corner-bottom")
          .hide();
      $.each(accordion.find("h3"), function(i, elem) {
          elem = $(elem);
          if (elem.data().load) {
              elem.click();
          }
      });
    }

    function genAll() {
        var hc = Highcharts.setOptions({
                global: {
                    useUTC: false
                },
                rangeSelector: {
                    buttons: [{
                        count: 1,
                        type: 'minute',
                        text: 'min'
                    }, {
                        count: 1,
                        type: 'hour',
                        text: 'hour'
                    }, {
                        type: 'all',
                        text: 'all'
                    }],
                    inputEnabled: false,
                },
                tooltip: {
                  valueDecimals: 3
                }
        });
        console.log('hc is', hc);
        $.getJSON('json/index.json', function(data) {
            console.log(data['run_info']);
            times = data['step_times'];
            $('#title').text($('title').text() + ' for ' + data['run_info']['var']['nodes'] + ' nodes.');
            allNames = data.views
            genAccordion(allNames);
        });
    }

    function main() {
        console.time('load_render_all');
        genAll();
    }

    main();

});
