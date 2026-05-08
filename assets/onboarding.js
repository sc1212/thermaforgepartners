(() => {
  const steps = [
    { label: 'Account setup', meta: 'Shop facts and operating rules' },
    { label: 'Call routing', meta: 'Forward to Frontline' },
    { label: 'First call recorded', meta: 'Recorded, reviewed, routed' },
    { label: 'Confirmation', meta: '24-hour review plan' },
  ];

  const state = {
    currentStep: 0,
    companyName: '',
    primaryContact: '',
    serviceArea: '',
    dispatchContact: '',
    emergencyRules: '',
    calendarOwner: '',
  };

  const stepper = document.querySelector('#stepper');
  const panels = Array.from(document.querySelectorAll('.step-panel'));
  const prevButton = document.querySelector('#prev-step');
  const nextButton = document.querySelector('#next-step');
  const completeButton = document.querySelector('#complete-onboarding');
  const meter = document.querySelector('#progress-meter');
  const eyebrow = document.querySelector('#step-eyebrow');
  const copyButton = document.querySelector('#copy-routing');
  const copyFeedback = document.querySelector('#copy-feedback');
  const form = document.querySelector('#step-form');

  const fallbackCopy = (text) => {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'fixed';
    textarea.style.top = '-9999px';
    document.body.appendChild(textarea);
    textarea.select();
    const copied = document.execCommand('copy');
    textarea.remove();
    return copied;
  };

  const updateStateFromInputs = () => {
    Array.from(form.elements).forEach((field) => {
      if (!field.name || field.type === 'checkbox') return;
      state[field.name] = field.value.trim();
    });
  };

  const updateSummaries = () => {
    updateStateFromInputs();
    const summaries = document.querySelectorAll('[data-summary]');
    summaries.forEach((node) => {
      const key = node.getAttribute('data-summary');
      const fallback = key === 'serviceArea' ? 'Service area pending' : key === 'dispatchContact' ? 'pending' : 'HVAC client setup';
      node.textContent = state[key] || fallback;
    });
  };

  const renderStepper = () => {
    stepper.innerHTML = steps.map((step, index) => `
      <li>
        <button type="button" data-testid="stepper-${index + 1}" data-step-target="${index}" ${index === state.currentStep ? 'aria-current="step"' : ''}>
          <span class="step-number">${index + 1}</span>
          <span><span class="step-label">${step.label}</span><span class="step-meta">${step.meta}</span></span>
        </button>
      </li>
    `).join('');
  };

  const showStep = (stepIndex) => {
    state.currentStep = Math.max(0, Math.min(stepIndex, steps.length - 1));
    panels.forEach((panel, index) => {
      panel.hidden = index !== state.currentStep;
    });
    prevButton.hidden = state.currentStep === 0;
    nextButton.hidden = state.currentStep >= steps.length - 2;
    completeButton.hidden = state.currentStep !== steps.length - 2;
    if (state.currentStep === steps.length - 1) {
      nextButton.hidden = true;
      completeButton.hidden = true;
    }
    eyebrow.textContent = `Step ${state.currentStep + 1} of ${steps.length} / ${steps[state.currentStep].label}`;
    meter.style.width = `${((state.currentStep + 1) / steps.length) * 100}%`;
    renderStepper();
    updateSummaries();
  };

  stepper.addEventListener('click', (event) => {
    const target = event.target.closest('[data-step-target]');
    if (!target) return;
    showStep(Number(target.dataset.stepTarget));
  });

  form.addEventListener('input', updateSummaries);
  prevButton.addEventListener('click', () => showStep(state.currentStep - 1));
  nextButton.addEventListener('click', () => showStep(state.currentStep + 1));
  completeButton.addEventListener('click', () => showStep(3));

  copyButton.addEventListener('click', async () => {
    const number = '615-785-9039';
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(number);
      } else if (!fallbackCopy(number)) {
        throw new Error('Clipboard unavailable');
      }
      copyFeedback.textContent = 'Copied 615-785-9039. Paste it into your carrier or phone-system forwarding screen.';
      copyButton.textContent = 'Copied';
    } catch (error) {
      copyFeedback.textContent = 'Copy was blocked. Select and copy 615-785-9039 manually.';
      copyButton.textContent = 'Copy number';
    }
  });

  showStep(0);
})();
