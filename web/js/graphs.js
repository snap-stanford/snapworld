$(function () {

    var PERC_AXIS = {'disk': true, 'network': true, 'cpu': true, 'max': true, 'mean': true};
    var MILLI_PER_SECOND = 1000;

    function getSeparateYaxis(series) {
        var yAxis = [];
        var axisInd = 1;
        yAxis.push({min: 0, max: 1.2});
        for (var i = 0; i < series.length; i++) {
            yAxis.push({
                labels: {
                    enabled: false
                }
            });
            series[i].yAxis = (series[i].name in PERC_AXIS) ? 0 : axisInd++;
        }
        return yAxis;
    }

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

    function padZero(num) {
        var res = '' + num;
        if (res.length === 1) {
            return '0' + res;
        } if (res.length !== 2) {
            console.error('Only expecting 0 <= num < 100, but I got: ' + res + '.');
        }
        return res;
    }

    function getYperfFileName(start) {
        return 'yperf-' + start.getFullYear() + padZero(start.getMonth() + 1) + padZero(start.getDate()) + '-' + padZero(start.getHours()) + '.json';
    }

    function getYperfFileRange(start, end) {
        var MILLI_SEC_PER_MIN = 60*1000;
        var PACIFIC_OFFSET = 8*60*MILLI_SEC_PER_MIN;
        var tOffset = start.getTimezoneOffset()*MILLI_SEC_PER_MIN;
        var fileList = [];
        if (tOffset !== PACIFIC_OFFSET) {
            console.log('Converting timezone to pacific.');
            start = new Date(start.getTime() - PACIFIC_OFFSET + tOffset);//TODO test
            end = new Date(end.getTime() - PACIFIC_OFFSET + tOffset);
        }
        var yperf_name;
        while (start < end) {
            yperf_name = getYperfFileName(start);
            fileList.push(yperf_name);
            //Move forward by an hour.
            start = new Date(start.getTime() + MILLI_SEC_PER_MIN * 60);
            console.log(start);
        }
        var last = getYperfFileName(end);
        if (yperf_name != last) {
            fileList.push(last);
        }
        return fileList;
    }

    function setVisible(json_series) {
        var VISIBLE = {'disk': true, 'network': true, 'cpu': true};
        for (var i = 0, len = json_series.length; i < len; i++) {
            var series = json_series[i];
            series.visible = series.name in VISIBLE;
        }
    }

    function renderGraph(json_response, name, times) {
        var series = json_response.series;
        setVisible(series);
        var yAxis = getSeparateYaxis(series);
        var plotLines = [];
        for (var i = 0, i_lim = times.length; i < i_lim; i++) {
            plotLines.push({
	    		value: (times[i] - times[0]) * MILLI_PER_SECOND,
	    		width: 1,
	    		color: 'green',
	    		dashStyle: 'dash',
	    		label: {
	    			text: 's' + i + ' end',
	    			align: 'right',
	    			y: 12,
	    			x: 0
	    		}
	    	});
        }
        $('#all_graphs > #' + name)
            .highcharts('StockChart', {
                legend: {
                    enabled: true
                },
                title: {
                    text: name
                },
                pointStart: (json_response.epoch_start - times[0]) * MILLI_PER_SECOND,
                pointInterval: MILLI_PER_SECOND,
                yAxis: yAxis,
                series: series,
                xAxis: {
                    min: 0,
                    max: (times[times.length - 1] - times[0]) * MILLI_PER_SECOND,
                    plotLines: plotLines}
                }
            );
    }

    function genInfoGraphs(times) {
        var first = new Date(times[0] * MILLI_PER_SECOND)
        var last = new Date(times[times.length - 1] * MILLI_PER_SECOND);
        console.log('start:', first);
        console.log('end;', last);
        console.log('length:', last - first)
        var ilnRange = ['max', 'avg', 'iln02', 'iln03', 'iln04', 'iln05'];
        var allGraphs = $('#all_graphs')
        for (var i = 0, i_lim = ilnRange.length; i < i_lim; i++) {
            allGraphs.append($('<div>', {style: "height: 500px; min-width: 500px",
              id:ilnRange[i]}))
            $.getJSON('json/' + ilnRange[i] + '.json', (function(name) {
            return function(data) {
                renderGraph(data, name, times);
                $(window).trigger('resize');
            };})(ilnRange[i])
            );
        }
    }

    function populateTable(data, div) {
      div.html('<table cellpadding="0" cellspacing="0" border="0" class="display"></table>');
      data.bFilter = false;
      data.iDisplayLength = 20;
      div.find('table').dataTable(data);
    }

    function getTables() {
      $.getJSON('json/sum_table.json', function(data) {
        populateTable(data, $('#sum_table'));
      });
       $.getJSON('json/avg_table.json', function(data) {
        populateTable(data, $('#avg_table'));
      });
    }

    function genCharts() {
        Highcharts.setOptions({
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
                    selected: 2
                },
                tooltipe: {
                  valueDecimals: 5
                },
                plotOption: {
                  area: {
                    dataGrouping: {
                      groupPixelWidth: 1000
                    }
                  }
                }
        });
        getTables()
        $.getJSON('json/index.json', function(data) {
            genInfoGraphs(data['step_times'])
        });
    }

    function main() {
        console.time('load_render_all');
        genCharts();
    }

    main();

});
