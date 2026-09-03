(function(){
  function h(v){return v==null?'':String(v);}
  function a(v){return String(v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
  function ajs(v){return String(v||'').replace(/\\/g,'\\\\').replace(/'/g,"\\'");}

  window.renderPlanejamento=function(){
    if(!window.PLAN_ITEMS) return;
    var q=(document.getElementById('planejamento-search').value||'').toLowerCase();
    var fPilar=document.getElementById('f-planejamento-pilar').value;
    var fPerfil=document.getElementById('f-planejamento-perfil').value;
    var html=''; var total=0, epq=0, ronan=0; var monthCounts={};
    var list=window.PLAN_ITEMS.slice().sort(function(a,b){return (a.MesID+a.Data).localeCompare(b.MesID+b.Data);});
    list.forEach(function(it){
      if(fPilar && it.Pilar!==fPilar) return;
      if(fPerfil && it.Perfil!==fPerfil) return;
      if(q && [it.ID,it.Headline,it.Tema,it.Pilar,it.Mes].join(' ').toLowerCase().includes(q)==false) return;
      total++; if(it.Perfil==='EPQ') epq++; if(it.Perfil==='Ronan') ronan++;
      monthCounts[it.Mes]=(monthCounts[it.Mes]||0)+1;
      var stClass=(it.Status||'Planejado').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'')==='publicado'?'st-positive':((it.Status||'Planejado').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'')==='agendar'||(it.Status||'Planejado').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'')==='aprovado')?'st-blue':'st-neutral';
      html+='<div class="sched-row" data-id="'+a(it.ID)+'">'
        +'<div class="sched-date"><span class="sched-dd">'+h(it.Data)+'</span></div>'
        +'<div class="sched-id">'+h(it.ID)+'</div>'
        +'<div class="sched-perfil '+(it.Perfil==='EPQ'?'perfil-epq':'perfil-ronan')+'">'+h(it.Perfil)+'</div>'
        +'<div class="sched-formato">'+h(it.Formato)+'</div>'
        +'<div class="sched-main"><div class="sched-headline">'+h(it.Headline)+'</div><div class="sched-tema">'+h(it.Tema)+'</div></div>'
        +'<div class="sched-pilar">'+h(it.Pilar)+'</div>'
        +'<div class="sched-status '+stClass+'"><span class="status-dot"></span>'+h(it.Status||'—')+'</div>'
      +'</div>';
    });
    document.getElementById('planejamento-rows').innerHTML=html;
    document.getElementById('planejamento-kpis').innerHTML='<div class="kpi-item"><div class="kpi-label">Planejados</div><div class="kpi-value featured">'+total+'</div></div>'
      +'<div class="kpi-item"><div class="kpi-label">EPQ</div><div class="kpi-value">'+epq+'</div></div>'
      +'<div class="kpi-item"><div class="kpi-label">Ronan</div><div class="kpi-value">'+ronan+'</div></div>'
      +'<div class="kpi-item"><div class="kpi-label">Meses</div><div class="kpi-value">'+Object.keys(monthCounts).length+'</div></div>';
  };

  window.renderPlanilha=function(){
    if(!window.PLAN_ITEMS) return;
    var manifest=window.__INTEGRATION_MANIFEST__||{};
    var links=manifest.links||{};
    var q=(document.getElementById('planilha-search').value||'').toLowerCase();
    var fStatus=document.getElementById('f-planilha-status').value;
    var html=''; var total=0;
    window.PLAN_ITEMS.slice().sort(function(a,b){return a.ID.localeCompare(b.ID);}).forEach(function(it){
      var link=links[it.ID]||{};
      if(fStatus && it.Status!==fStatus) return;
      if(q && [it.ID,it.Headline,it.Tema,it.Mes,(link.owner||'')].join(' ').toLowerCase().includes(q)==false) return;
      total++;
      var taskId=link.taskId?'<a href="tarefas.html" target="_blank" rel="noopener">Tarefa '+a(link.taskId)+'</a>':'—';
      var drive=link.drivePath?'<a href="x-apple.systemfile://'+encodeURI(link.drivePath)+'">Abrir</a>':'—';
      html+='<div class="sched-row" data-id="'+a(it.ID)+'">'
        +'<div class="sched-id">'+h(it.ID)+'</div>'
        +'<div class="sched-date">'+h(it.Data)+'</div>'
        +'<div class="sched-perfil '+(it.Perfil==='EPQ'?'perfil-epq':'perfil-ronan')+'">'+h(it.Perfil)+'</div>'
        +'<div class="sched-formato">'+h(it.Formato)+'</div>'
        +'<div class="sched-main"><div class="sched-headline">'+h(it.Headline)+'</div><div class="sched-tema">'+h(it.Tema)+'</div></div>'
        +'<div class="sched-pilar">'+h(it.Pilar)+'</div>'
        +'<div class="sched-status st-neutral"><span class="status-dot"></span>'+h(it.Status||'—')+'</div>'
        +'<div>'+taskId+'</div>'
        +'<div>'+drive+'</div>'
      +'</div>';
    });
    document.getElementById('planilha-rows').innerHTML=html;
    document.getElementById('planilha-kpis').innerHTML='<div class="kpi-item"><div class="kpi-label">Itens</div><div class="kpi-value featured">'+total+'</div></div>';
  };

  window.switchView=function(view){
    document.querySelectorAll('.tab[data-view]').forEach(function(btn){ btn.classList.toggle('active', btn.dataset.view===view); });
    ['acompanhamento','planejamento','planilha'].forEach(function(name){
      var el=document.getElementById('view-'+name);
      if(!el) return;
      el.style.display=name===view?'':'none';
    });
  };

  window.bindPlugins=function(){
    ['planejamento-search','f-planejamento-pilar','f-planejamento-perfil'].forEach(function(id){
      var el=document.getElementById(id); if(!el) return;
      el.addEventListener('input', window.renderPlanejamento);
      el.addEventListener('change', window.renderPlanejamento);
    });
    ['planilha-search','f-planilha-status'].forEach(function(id){
      var el=document.getElementById(id); if(!el) return;
      el.addEventListener('input', window.renderPlanilha);
      el.addEventListener('change', window.renderPlanilha);
    });
    document.querySelectorAll('.tab[data-view]').forEach(function(btn){
      btn.addEventListener('click', function(){ window.switchView(btn.dataset.view); });
    });
  };
})();
