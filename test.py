import streamlit as st
import streamlit.components.v1 as components

# --- CSS ---
st.markdown("""
<style>
/* Streamlit içerik üstte kalsın */
.stApp {
    position: relative;
    z-index: 1;
}

/* Canvas / ağ efekti tam ekran, saydam layer */
.network-background {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 0;  /* İçerik üstte, canvas altta */
    pointer-events: none; /* Fare ile etkileşim yok */
}
</style>

<canvas class="network-background" id="network-canvas"></canvas>
""", unsafe_allow_html=True)

# --- JS Canvas ---
components.html("""
<script>
const canvas = document.getElementById('network-canvas');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const particles = [];
const particleCount = 60;
for(let i=0;i<particleCount;i++){
    particles.push({
        x: Math.random()*canvas.width,
        y: Math.random()*canvas.height,
        vx: (Math.random()-0.5)*0.7,
        vy: (Math.random()-0.5)*0.7
    });
}

function animate(){
    // Gradient arka plan
    const gradient = ctx.createLinearGradient(0,0,canvas.width,canvas.height);
    gradient.addColorStop(0,"#ffffff");
    gradient.addColorStop(0.33,"#cce6ff");
    gradient.addColorStop(0.66,"#99ccff");
    gradient.addColorStop(1,"#66b3ff");
    ctx.fillStyle = gradient;
    ctx.fillRect(0,0,canvas.width,canvas.height);

    // Noktaları çiz
    for(let i=0;i<particles.length;i++){
        const p = particles[i];
        p.x += p.vx;
        p.y += p.vy;

        if(p.x<0||p.x>canvas.width) p.vx*=-1;
        if(p.y<0||p.y>canvas.height) p.vy*=-1;

        ctx.fillStyle="#a3cfff";
        ctx.beginPath();
        ctx.arc(p.x,p.y,3,0,Math.PI*2);
        ctx.fill();
    }

    // Çizgileri çiz
    for(let i=0;i<particles.length;i++){
        for(let j=i+1;j<particles.length;j++){
            const dx = particles[i].x - particles[j].x;
            const dy = particles[i].y - particles[j].y;
            const dist = Math.sqrt(dx*dx + dy*dy);
            if(dist<150){
                ctx.strokeStyle="rgba(163,207,255,0.3)";
                ctx.lineWidth=1;
                ctx.beginPath();
                ctx.moveTo(particles[i].x,particles[i].y);
                ctx.lineTo(particles[j].x,particles[j].y);
                ctx.stroke();
            }
        }
    }

    requestAnimationFrame(animate);
}
animate();

window.addEventListener('resize', ()=>{
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});
</script>
""", height=0)

# --- Streamlit içerik ---
st.title("Modern Arka Plan Görünümü")
st.write("Bu yazılar ağ efekti layer’ının üstünde duruyor.")
st.button("Test Butonu")
st.write("Görsel olarak arka plan gibi, ama Streamlit sınırlamaları nedeniyle layer üstünde.")
