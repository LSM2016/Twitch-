(function () {
    'use strict';

    var inputFile;
    var filesElement;
    var Logger;

    function LogOutput(text) {
        Logger.set(Logger.num++, text);
    }

    var lastCommand;

    function LogNewCommand(name, text) {
        LogEndCommand(0);
        lastCommand = `${name}-${Logger.num}`;
        LogOutput(`fold:start:${lastCommand}\x1B\[K\n`);
        LogOutput(text);
    }

    function LogEndCommand(exitCode) {
        if (lastCommand) {
            LogOutput(`exit code: ${exitCode}\nfold:end:${lastCommand}\x1B\[K\n`);
        }
        lastCommand = undefined;
    }

    function IsSupported() {
        return document.querySelector && window.URL && window.Worker;
    }

    function parseArguments(text) {
        text = text.replace(/\s+/g, ' ');
        var args = [];
        // Allow double quotes to not split args.
        text.split('"').forEach(function (t, i) {
            t = t.trim();
            if ((i % 2) === 1) {
                args.push(t);
            } else {
                args = args.concat(t.split(" "));
            }
        });
        return args;
    }

    // 使用ffmpeg.js裁剪并转码
    function RunMp4Conversion() {
        // 将转换按钮置不可点击 防止误操作
        document.getElementById("convertmp4").setAttribute("disable", true)

        if (!inputFile)
            return alert('需要选择一个视频文件!');

        var startTime = document.getElementById("start").value;
        var duration = document.getElementById("duration").value;

        var inputName = inputFile.name;

        var reader = new FileReader();

        reader.addEventListener("loadend", function () {
            var createMp4Command =
                `-hide_banner -ss ${startTime} -t ${duration} -i "${inputName}" -pix_fmt yuv420p -b:v 6000k -strict -2 -y output.mp4`;

            // 打开进度条
            EnableOrDisableProgressBar(true);
            var progress_bar = document.getElementById("progress-bar");
            document.getElementById("progress-bar").setAttribute("aria-valuenow", 0);
            document.getElementById("progress-bar").style.width = "0%";
            RunCommand(
                {
                    text: createMp4Command,
                    data: [{name: inputName, data: new Uint8Array(reader.result)}],
                    prettyName: 'convert-to-mp4'
                },
                function (err, buffers) {
                    if (err)
                        throw err;
                    buffers.forEach(function (file) {
                        filesElement.appendChild(
                            getDownloadLink(file.data, file.name, 'video/mp4'));
                    });
                    LogOutput(`\n文件 ${inputName}  转换完成`);
                    document.getElementById("progress-bar").innerText = "转换完成";
                    document.getElementById("progress-bar").setAttribute("aria-valuenow", 100);
                    document.getElementById("progress-bar").style.width = "100%";

                    // 关闭进度条
                    EnableOrDisableProgressBar(false);
                    // 恢复按钮点击状态
                    document.getElementById("convertmp4").setAttribute("disable", false)
                    //window.setTimeout(EnableOrDisableProgressBar(false),5000);
                });
        });
        reader.readAsArrayBuffer(inputFile);
    }

    function EnableOrDisableProgressBar(enable_bar) {
        if (enable_bar) {
            document.getElementById("progress-bar1").style.display = "";
        } else {
            document.getElementById("progress-bar1").style.display = "none";
        }
    }

    function RunGifConversion() {
        if (!inputFile)
            return alert('You need to select a source file!');

        var startTime = document.getElementById("start").value;
        var duration = document.getElementById("duration").value;
        var scale = document.getElementById("scale").value;
        var fps = document.getElementById("fps").value;
        var palette = 'palette.jpg';
        var filters = `fps=${fps},scale=${scale}:-1:flags=lanczos`;

        var inputName = inputFile.name;

        var reader = new FileReader();

        reader.addEventListener("loadend", function () {
            var createPaletteCommand =
                `-hide_banner -ss ${startTime} -t ${duration} -i "${inputName}"
       -vf "${filters}, palettegen" -y ${palette}`;

            var createGifCommand =
                `-hide_banner -ss ${startTime} -t ${duration} -i "${inputName}"
       -i ${palette} -lavfi "${filters} [x]; [x][1:v] paletteuse"
       -y output.gif`;

            RunCommand(
                {
                    text: createPaletteCommand,
                    data: [{name: inputName, data: new Uint8Array(reader.result)}],
                    prettyName: 'gif-palettegen'
                },
                function (err, buffers) {
                    if (err)
                        throw err;
                    if (buffers.length === 0)
                        LogOutput('\nFailed to generate palette for ' + inputName);

                    RunCommand(
                        {
                            text: createGifCommand,
                            prettyName: 'convert-to-gif',
                            data: [
                                {name: inputName, data: new Uint8Array(reader.result)},
                                {name: buffers[0].name, data: buffers[0].data}
                            ]
                        },
                        function (err, buffers) {
                            if (err)
                                throw err;
                            buffers.forEach(function (file) {
                                filesElement.appendChild(
                                    getDownloadLink(file.data, file.name));
                            });
                            LogOutput(`\nConverted ${inputName} to gif!`);
                        });
                });
        });
        reader.readAsArrayBuffer(inputFile);
    }

    function GetRandomInt(min, max) {
        return Math.floor(Math.random() * (max - min)) + min;
    }

    // 获取待剪辑视频并设置相关信息
    function getDownloadLink(fileData, fileName, fileType) {
        if (fileData instanceof Blob) {
            var blob = fileData;
            var src = window.URL.createObjectURL(fileData);
        } else {
            var blob = new Blob([fileData]);
            var src = window.URL.createObjectURL(blob);
        }

        document.getElementById("preview-card").style.display = "";
        var preview_title = document.getElementById("preview-title");

        var container = document.createElement('div');
        container.className = 'row card-body';
        container.id = 'newContainer'

        var col1 = document.createElement('div');
        //col1.className = 'col-md-8';


        var col2 = document.createElement('div');
        col2.className = 'col-md-4';
        col2.style.display = 'none';
        preview_title.textContent = fileName;

        //创建完整视频上传按钮
        var downloadLink = document.createElement('a');
        downloadLink.download = fileName;
        downloadLink.href = src;
        downloadLink.className = 'btn btn-lg btn-primary col1';
        downloadLink.textContent = '上传完整视频';

        col2.appendChild(downloadLink);


        if (fileName.match(/\.jpeg|\.gif|\.jpg|\.png/)) {
            var img = document.createElement('img');
            img.src = src;
            img.className = 'img-thumbnail';
            col1.appendChild(img);
        } else {
            var video = document.createElement('video');
            video.controls = true;
            video.width = 560;
            video.height = 315;
            video.id = 'preview-video-' + (Math.random() * 1000).toFixed(0);
            video.className = 'video-js vjs-default-skin';

            var source = document.createElement('source');
            source.src = src;
            source.type = fileType || fileData.type;
            video.appendChild(source);

            var picker = document.getElementById('uploader-picker');
            picker.style = "display:none"

            col1.appendChild(video);
        }

        container.appendChild(col1);
        container.appendChild(col2);
        document.getElementById("tool-group1").appendChild(col2);
        return container;
    }

    function RunCommand(options, cb) {
        var worker = new Worker("/static/assets/js/ffmpeg-worker-webm.js");
        var lastError;

        worker.onmessage = function (event) {
            var message = event.data;

            var clip_duration = document.getElementById('duration').value;
            switch (message.type) {
                case 'ready':
                    break;
                case 'stdout':
                    //LogOutput(message.data + "\n");
                    break;
                case 'stderr':
                    //LogOutput(message.data + "\n");
                    if (message.data.lastIndexOf('time=') > 0) {
                        // 转换进度条处理
                        var index = message.data.lastIndexOf("time=") + 5;
                        var timer = message.data.substring(index, index + 11);

                        var hour_str = timer.split(':')[0];
                        var min_str = timer.split(':')[1];
                        var sec_str = timer.split(':')[2];
                        var total_seconds = parseFloat(hour_str) * 60 * 60 + parseFloat(min_str) * 60 + parseFloat(sec_str);

                        var percentage = total_seconds / clip_duration * 100;

                        document.getElementById("progress-bar").setAttribute("aria-valuenow", percentage);
                        document.getElementById("progress-bar").style.width = percentage.toString() + "%";
                    }
                    break;
                case 'start':
                    break;
                case 'done':
                    var buffers = message.data.MEMFS;
                    if (cb)
                        cb(lastError, buffers);
                    worker.terminate();
                    break;
                case 'exit':
                    LogEndCommand(message.data);
                    if (message.data > 0)
                        lastError = new Error(`exit code: ${message.data}`);
                    break;
                case 'run':
                    break;
                default:
                    throw new Error('Unhandled switch case', message.type);
            }
        };

        var args = parseArguments(options.text);
        LogNewCommand(options.prettyName || args[0],
            '$ ffmpeg ' + args.join(' ') + '\n');
        worker.postMessage({type: "run", arguments: args, MEMFS: options.data});
    }

    // 打开视频文件相关
    function handleFileSelect(evt) {
        document.getElementById('inputpreview').innerHTML = '';

        var files = evt.target.files; // FileList object
        if (files.length === 0)
            return;
        inputFile = files[0];

        var newElement = getDownloadLink(inputFile, inputFile.name);
        document.getElementById('inputpreview').appendChild(newElement);
        if (inputFile.name.match(/\.jpeg|\.gif|\.jpg|\.png/)) return;
        var videoPlayer = videojs(newElement.firstChild.firstChild.id);
        videoPlayer.rangeslider();
        videoPlayer.ready(function () {
            // 默认播放器音量为50
            videoPlayer.volume(50);
            videoPlayer.play();
            videoPlayer.hideControlTime();
            videoPlayer.on('sliderchange', function () {
                var values = videoPlayer.getValueSlider();
                document.getElementById('start').value = values.start.toFixed(2);
                document.getElementById('duration').value = (values.end - values.start).toFixed(2);
            });
            videoPlayer.on('loadedRangeSlider', function () {
                videoPlayer.pause();
                videoPlayer.setValueSlider(0, 30);
            });
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        if (!IsSupported()) {
            alert(`不支持当前浏览器，请使用Chrome和Firefox!`);
            return;
        }

        document.getElementById('picker')
            .addEventListener('change', handleFileSelect, false);

        filesElement = document.querySelector("#outputfiles");
        /*
        document.getElementById('uploadForm')
            .onsubmit = function (e) {
            return false;
        };
        */

        $('#convertgif')
            .on('click', function (e) {
                RunGifConversion();
                return true;
            });

        $('#convertmp4')
            .on('click', function (e) {
                RunMp4Conversion();
                return true;
            });

        Logger = Log.create();
        Logger.num = 0;
        LogOutput('Loading JavaScript files (it may take a minute)\n');

        window.onerror = function (msg, url, line, col, error) {
            LogOutput(`\n${msg} line: ${line} col: ${col} url: ${url}\n`);
        };

        $('#log')
            .on('click', '.fold',
                function () {
                    return $(this).toggleClass('open');
                });

        RunCommand({text: '-version -hide_banner'}, function (err) {
            if (err)
                throw err;
            RunCommand({text: '-formats -hide_banner'}, function (err) {
                if (err)
                    throw err;
                LogOutput('Sample commands executing fine!');
            });
        });
    });
})();