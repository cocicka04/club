document.addEventListener('DOMContentLoaded', function(){
    const cat = document.getElementById('id_category');
    const tariff = document.getElementById('id_tariff');
    if(!cat || !tariff) return;
  
    cat.addEventListener('change', () => {
      const selected = cat.value;
      for(let opt of tariff.options){
        if(opt.dataset.category && selected && opt.dataset.category !== selected){
          opt.style.display = 'none';
        } else {
          opt.style.display = 'block';
        }
      }
    });
  });
  