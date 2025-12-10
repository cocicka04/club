document.addEventListener('DOMContentLoaded', function(){
    const hoursInput = document.querySelector('input[name="hours"]');
    const placeSelect = document.querySelector('select[name="place"]');
    const totalEl = document.getElementById('total-price');
  
    function updatePrice(){
      const hours = parseInt(hoursInput ? hoursInput.value : 1);
      const sel = placeSelect;
      if(!sel) return;
      const option = sel.options[sel.selectedIndex];
      // в option должны быть data-price атрибуты (см. форма рендер)
      const price = parseFloat(option.dataset.price || 0);
      const total = (price * hours).toFixed(2);
      totalEl.textContent = total;
    }
  
    if(hoursInput) hoursInput.addEventListener('input', updatePrice);
    if(placeSelect) placeSelect.addEventListener('change', updatePrice);
    updatePrice();
  });
  