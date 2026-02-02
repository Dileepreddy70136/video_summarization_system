// Premium UI JavaScript

document.addEventListener('DOMContentLoaded', function () {
  // File Upload Handling
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('videoFile');
  const uploadForm = document.getElementById('uploadForm');
  const processBtn = document.getElementById('processBtn');

  // Click to upload
  if (dropZone && fileInput) {
    dropZone.addEventListener('click', () => {
      fileInput.click();
    });

    // Drag and drop
    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
      dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('dragover');

      const files = e.dataTransfer.files;
      if (files.length > 0) {
        fileInput.files = files;
        updateFileName(files[0].name);
      }
    });

    // File selected
    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        updateFileName(e.target.files[0].name);
      }
    });
  }

  function updateFileName(name) {
    const uploadTitle = document.querySelector('.upload-title');
    if (uploadTitle) {
      uploadTitle.textContent = `Selected: ${name}`;
      dropZone.style.borderColor = '#667eea';
      dropZone.style.background = 'rgba(102, 126, 234, 0.05)';
    }
  }

  // Form submission
  if (uploadForm && processBtn) {
    uploadForm.addEventListener('submit', (e) => {
      if (!fileInput.files.length) {
        e.preventDefault();
        alert('Please select a video file first!');
        return;
      }

      // Show loading state
      processBtn.classList.add('processing');
      processBtn.querySelector('.btn-text').textContent = 'Processing Video...';
      processBtn.disabled = true;

      showProgress('Analyzing video content. This may take a minute...');
    });
  }

  // YouTube Form Handling
  const youtubeForm = document.getElementById('youtubeForm');
  const btnYoutube = document.getElementById('btnYoutube');
  if (youtubeForm && btnYoutube) {
    youtubeForm.addEventListener('submit', (e) => {
      const url = youtubeForm.querySelector('input[name="youtube_url"]').value;
      if (!url) {
        e.preventDefault();
        alert('Please paste a YouTube link first!');
        return;
      }

      btnYoutube.classList.add('processing');
      btnYoutube.querySelector('.btn-text').textContent = 'Extracting...';
      btnYoutube.disabled = true;

      showProgress('Fetching YouTube transcript and generating summary...');
    });
  }

  // Tab Switching
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabId = btn.getAttribute('data-tab');

      // Update buttons
      tabBtns.forEach(b => {
        b.classList.remove('active');
        b.style.background = 'transparent';
        b.style.color = 'var(--text-light)';
      });
      btn.classList.add('active');
      btn.style.background = 'var(--primary)';
      btn.style.color = 'white';

      // Update contents
      tabContents.forEach(content => {
        if (content.getAttribute('data-tab') === tabId) {
          content.style.display = 'block';
        } else {
          content.style.display = 'none';
        }
      });
    });
  });

  // Smooth scroll for navigation
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });

  // Animate elements on scroll
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, observerOptions);

  document.querySelectorAll('.feature-card, .result-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(30px)';
    card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(card);
  });

  // Copy to clipboard function
  window.copyToClipboard = function (text) {
    navigator.clipboard.writeText(text).then(() => {
      // Show success feedback
      const btn = event.target;
      const originalText = btn.textContent;
      btn.textContent = 'Copied!';
      btn.style.background = '#43e97b';

      setTimeout(() => {
        btn.textContent = originalText;
        btn.style.background = '';
      }, 2000);
    });
  };

  // Add parallax effect to background
  window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const bgGradient = document.querySelector('.bg-gradient');
    if (bgGradient) {
      bgGradient.style.transform = `translateY(${scrolled * 0.5}px)`;
    }
  });

  // Video player controls enhancement
  document.querySelectorAll('video').forEach(video => {
    video.addEventListener('loadedmetadata', function () {
      console.log('Video loaded:', this.duration);
    });
  });
});

// Progress indicator for long-running tasks
function showProgress(message) {
  // Create progress overlay
  const overlay = document.createElement('div');
  overlay.className = 'progress-overlay';
  overlay.innerHTML = `
    <div class="progress-card glass">
      <div class="progress-loader"></div>
      <p class="progress-text">${message}</p>
    </div>
  `;

  // Add styles if not exists
  if (!document.getElementById('progress-styles')) {
    const style = document.createElement('style');
    style.id = 'progress-styles';
    style.textContent = `
      .progress-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        animation: fadeIn 0.3s ease;
      }
      .progress-card {
        padding: 40px;
        border-radius: 20px;
        text-align: center;
      }
      .progress-loader {
        width: 60px;
        height: 60px;
        border: 4px solid rgba(102, 126, 234, 0.2);
        border-top-color: #667eea;
        border-radius: 50%;
        margin: 0 auto 20px;
        animation: spin 0.8s linear infinite;
      }
      .progress-text {
        font-size: 16px;
        font-weight: 600;
        color: var(--text-dark);
      }
      @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
      }
    `;
    document.head.appendChild(style);
  }

  document.body.appendChild(overlay);

  return overlay;
}

function hideProgress(overlay) {
  if (overlay) {
    overlay.style.animation = 'fadeOut 0.3s ease';
    setTimeout(() => overlay.remove(), 300);
  }
}
