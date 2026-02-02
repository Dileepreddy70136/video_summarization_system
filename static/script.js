(function () {
  'use strict';

  // ----- Main Tab Navigation -----
  var mainTabs = document.querySelectorAll('.main-tab');
  var tabContents = document.querySelectorAll('.tab-content');

  mainTabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      var tabName = tab.getAttribute('data-tab');

      // Remove active class from all tabs
      mainTabs.forEach(function (t) {
        t.classList.remove('active');
      });

      // Hide all tab contents
      tabContents.forEach(function (content) {
        content.classList.remove('active');
      });

      // Activate clicked tab
      tab.classList.add('active');

      // Show corresponding content
      var targetContent = document.getElementById('tab-' + tabName);
      if (targetContent) {
        targetContent.classList.add('active');

        // Auto-focus YouTube URL input when switching to YouTube tab
        if (tabName === 'youtube') {
          var ytInput = document.getElementById('youtubeUrl');
          if (ytInput) {
            setTimeout(function () {
              ytInput.focus();
            }, 200);
          }
        }
      }
    });
  });

  // ----- Drop Zone -----
  var dropZone = document.getElementById('dropZone');
  var fileInput = document.getElementById('videoFile');

  if (dropZone && fileInput) {
    dropZone.addEventListener('click', function () {
      fileInput.click();
    });

    dropZone.addEventListener('dragover', function (e) {
      e.preventDefault();
      dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', function () {
      dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', function (e) {
      e.preventDefault();
      dropZone.classList.remove('dragover');

      var file = e.dataTransfer && e.dataTransfer.files[0];
      if (file && file.type.startsWith('video/')) {
        fileInput.files = e.dataTransfer.files;
        var hintElement = dropZone.querySelector('.hint');
        if (hintElement) {
          hintElement.textContent = file.name;
        }
      }
    });

    fileInput.addEventListener('change', function () {
      var fileName = fileInput.files && fileInput.files[0] && fileInput.files[0].name;
      var hintElement = dropZone.querySelector('.hint');
      if (hintElement) {
        hintElement.textContent = fileName || 'MP4, AVI, MOV, WebM, etc.';
      }
    });
  }

  // ----- Form Submit: Loading State -----
  var videoForm = document.getElementById('videoForm');
  var btnVideo = document.getElementById('btnVideo');

  if (videoForm && btnVideo) {
    videoForm.addEventListener('submit', function (e) {
      // Check if a file is selected
      if (!fileInput || !fileInput.files || !fileInput.files.length) {
        e.preventDefault();
        alert('Please choose a video file first.');
        return;
      }

      // Check if at least one option is selected
      var hasOption = false;
      var checkboxes = videoForm.querySelectorAll('input[type="checkbox"]');
      checkboxes.forEach(function (cb) {
        if (cb.checked) hasOption = true;
      });

      if (!hasOption) {
        e.preventDefault();
        alert('Please select at least one processing option.');
        return;
      }

      // Show loading state
      btnVideo.disabled = true;
      btnVideo.innerHTML = '<span class="spinner"></span> Processing…';
    });
  }

  var youtubeForm = document.getElementById('youtubeForm');
  var btnYoutube = document.getElementById('btnYoutube');

  if (youtubeForm && btnYoutube) {
    youtubeForm.addEventListener('submit', function (e) {
      var urlInput = document.getElementById('youtubeUrl');
      var url = urlInput ? urlInput.value.trim() : '';

      if (!url) {
        e.preventDefault();
        alert('Please enter a YouTube URL first.');
        return;
      }

      // Show loading state
      btnYoutube.disabled = true;
      btnYoutube.innerHTML = '<span class="spinner"></span> Processing…';
    });
  }

  // ----- Copy Buttons -----
  document.querySelectorAll('[data-copy]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var id = btn.getAttribute('data-copy');
      var el = document.getElementById(id);
      if (!el) return;

      var text = el.textContent || '';

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () {
          var originalText = btn.textContent;
          btn.textContent = 'Copied!';
          setTimeout(function () {
            btn.textContent = originalText;
          }, 1500);
        }).catch(function () {
          // Fallback
          copyToClipboardFallback(text, btn);
        });
      } else {
        copyToClipboardFallback(text, btn);
      }
    });
  });

  function copyToClipboardFallback(text, btn) {
    var textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    try {
      document.execCommand('copy');
      var originalText = btn.textContent;
      btn.textContent = 'Copied!';
      setTimeout(function () {
        btn.textContent = originalText;
      }, 1500);
    } catch (err) {
      console.error('Copy failed:', err);
    }
    document.body.removeChild(textarea);
  }

  // ----- SRT Download -----
  var srtData = document.getElementById('srtData');
  var downloadSrt = document.getElementById('downloadSrt');

  if (srtData && downloadSrt) {
    downloadSrt.addEventListener('click', function (e) {
      e.preventDefault();
      var srt = srtData.textContent || '';
      var blob = new Blob([srt], { type: 'text/plain;charset=utf-8' });
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'captions.srt';
      a.click();
      URL.revokeObjectURL(a.href);
    });
  }
})();
