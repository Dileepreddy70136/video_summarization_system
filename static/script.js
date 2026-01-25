(function () {
  'use strict';

  // ----- Tabs -----
  var btns = document.querySelectorAll('.tab-btn');
  var panels = document.querySelectorAll('.tab-panel');

  function setActive(name) {
    btns.forEach(function (b) {
      b.classList.toggle('is-active', b.getAttribute('data-tab') === name);
    });
    panels.forEach(function (p) {
      p.classList.toggle('is-active', p.id === 'panel-' + name);
    });
  }

  btns.forEach(function (b) {
    b.addEventListener('click', function () {
      setActive(b.getAttribute('data-tab'));
    });
  });
  setActive('video');

  // ----- Drop zone -----
  var dz = document.getElementById('dropZone');
  var inp = document.getElementById('videoFile');
  if (dz && inp) {
    dz.addEventListener('click', function () { inp.click(); });
    dz.addEventListener('dragover', function (e) { e.preventDefault(); dz.classList.add('dragover'); });
    dz.addEventListener('dragleave', function () { dz.classList.remove('dragover'); });
    dz.addEventListener('drop', function (e) {
      e.preventDefault();
      dz.classList.remove('dragover');
      var f = e.dataTransfer && e.dataTransfer.files[0];
      if (f && f.type.startsWith('video/')) {
        inp.files = e.dataTransfer.files;
        dz.querySelector('.hint').textContent = f.name;
      }
    });
    inp.addEventListener('change', function () {
      var n = inp.files && inp.files[0] && inp.files[0].name;
      if (dz && dz.querySelector('.hint')) dz.querySelector('.hint').textContent = n || 'MP4, AVI, MOV, WebM, etc.';
    });
  }

  // ----- Copy buttons -----
  document.querySelectorAll('[data-copy]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var id = btn.getAttribute('data-copy');
      var el = document.getElementById(id);
      if (!el) return;
      var t = el.textContent || '';
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(t).then(function () {
          var orig = btn.textContent;
          btn.textContent = 'Copied!';
          setTimeout(function () { btn.textContent = orig; }, 1500);
        });
      } else {
        var ta = document.createElement('textarea');
        ta.value = t;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        var orig = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(function () { btn.textContent = orig; }, 1500);
      }
    });
  });

  // ----- SRT download -----
  var srtEl = document.getElementById('srtData');
  var dlBtn = document.getElementById('downloadSrt');
  if (srtEl && dlBtn) {
    dlBtn.addEventListener('click', function (e) {
      e.preventDefault();
      var srt = srtEl.textContent || '';
      var blob = new Blob([srt], { type: 'text/plain;charset=utf-8' });
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'captions.srt';
      a.click();
      URL.revokeObjectURL(a.href);
    });
  }

  // ----- Form submit: loading state -----
  var formVideo = document.getElementById('form-video');
  var btnVideo = document.getElementById('btnVideo');
  if (formVideo && btnVideo) {
    formVideo.addEventListener('submit', function (e) {
      var f = document.getElementById('videoFile');
      var sum = formVideo.querySelector('[name="do_summary"]');
      var cap = formVideo.querySelector('[name="do_caption"]');
      var need = (sum && sum.checked) || (cap && cap.checked);
      if (need && f && (!f.files || !f.files.length)) {
        e.preventDefault();
        alert('Please choose a video file first.');
        return;
      }
      if (f && f.files && f.files.length) {
        btnVideo.disabled = true;
        btnVideo.innerHTML = '<span class="spinner"></span> Processing…';
      }
    });
  }
})();
