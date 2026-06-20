const INITIAL_MATCHES = [
    {
        id: 'm_1_1',
        week: 1,
        homeTeam: 'Real Madrid',
        awayTeam: 'Barcelona',
        time: '20:00',
        odds: { '1': 1.85, 'X': 3.60, '2': 3.80 },
        oddsPoints: { '1': '+2', 'X': '+4', '2': '+4' },
    },
    {
        id: 'm_1_2',
        week: 1,
        homeTeam: 'Galatasaray',
        awayTeam: 'Fenerbahçe',
        time: '21:00',
        odds: { '1': 1.90, 'X': 3.40, '2': 3.60 },
        oddsPoints: { '1': '+2', 'X': '+3', '2': '+4' },
    }
];

function renderMatches() {
    const container = document.getElementById('matches-list-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    INITIAL_MATCHES.forEach(match => {
        const cardHTML = `
<div class="w-full max-w-[520px] mx-auto px-4 mb-8">

    <div class="bg-[#121b2d]/40 backdrop-blur-xl border border-white/[0.06] rounded-[24px] p-5 mb-4 text-white font-sans antialiased">
        
        <div class="flex justify-between items-center text-[10px] text-zinc-400 font-bold tracking-widest uppercase mb-5">
            <div class="flex items-center gap-2">
                <span class="w-1.5 h-1.5 bg-emerald-500 rounded-full"></span>
                <span>Trendyol Süper Lig</span>
            </div>
            <span class="text-zinc-500">${match.week}. Hafta</span>
        </div>

        <div class="flex items-center justify-between mb-6">
            <div class="w-[40%] text-left font-black text-base tracking-tight text-white uppercase">
                ${match.homeTeam}
            </div>
            
            <div class="w-[20%] flex flex-col items-center justify-center">
                <span class="text-[9px] text-zinc-500 font-bold uppercase tracking-wider mb-1">Başlamadı</span>
                <span class="text-sm font-black tracking-tight bg-white/[0.05] border border-white/[0.08] px-3 py-1 rounded-xl text-zinc-200">
                    ${match.time}
                </span>
            </div>
            
            <div class="w-[40%] text-right font-black text-base tracking-tight text-white uppercase">
                ${match.awayTeam}
            </div>
        </div>

        <div class="border-t border-b border-white/[0.04] py-3.5 my-5">
            <div class="grid grid-cols-3 text-center divide-x divide-white/[0.06]">
                <div class="flex flex-col">
                    <span class="text-[9px] text-zinc-500 font-bold uppercase tracking-wider">MS1</span>
                    <span class="text-xs font-black mt-1 text-zinc-200">${match.odds['1'].toFixed(2)} <span class="text-[10px] text-emerald-400 font-medium ml-0.5">(${match.oddsPoints['1']})</span></span>
                </div>
                <div class="flex flex-col">
                    <span class="text-[9px] text-zinc-500 font-bold uppercase tracking-wider">MSX</span>
                    <span class="text-xs font-black mt-1 text-zinc-200">${match.odds['X'].toFixed(2)} <span class="text-[10px] text-emerald-400 font-medium ml-0.5">(${match.oddsPoints['X']})</span></span>
                </div>
                <div class="flex flex-col">
                    <span class="text-[9px] text-zinc-500 font-bold uppercase tracking-wider">MS2</span>
                    <span class="text-xs font-black mt-1 text-zinc-200">${match.odds['2'].toFixed(2)} <span class="text-[10px] text-emerald-400 font-medium ml-0.5">(${match.oddsPoints['2']})</span></span>
                </div>
            </div>
        </div>

        <div class="flex items-center justify-between bg-white/[0.02] border border-white/[0.04] p-2.5 rounded-xl mb-5">
            <div class="flex items-center gap-1">
                <span class="text-[11px] text-zinc-400 font-semibold mr-1.5 ml-1">Tahminin:</span>
                <button class="w-7 h-7 bg-white text-black font-black rounded-lg text-xs">1</button>
                <button class="w-7 h-7 hover:bg-white/5 font-bold rounded-lg text-xs text-zinc-500">X</button>
                <button class="w-7 h-7 hover:bg-white/5 font-bold rounded-lg text-xs text-zinc-500">2</button>
            </div>
            
            <div class="flex items-center gap-2">
                <select class="bg-[#0b101d] border border-white/[0.06] rounded-lg px-2.5 py-1 text-xs font-bold text-zinc-300 focus:outline-none cursor-pointer">
                    <option>1 Fark</option>
                    <option>2 Fark</option>
                    <option>3+ Fark</option>
                </select>
                <span class="text-[11px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2.5 py-1 rounded-lg font-bold">✓ Kaydedildi</span>
            </div>
        </div>

        <div class="flex flex-wrap gap-1.5 pt-1">
            <div class="bg-white/[0.02] border border-white/[0.04] px-2.5 py-1 rounded-full flex items-center gap-1.5 text-[11px] text-zinc-400">
                <span class="font-medium">Ahmet</span>
                <span class="text-[9px] text-zinc-600 font-bold uppercase tracking-wider">🔒 Kilitli</span>
            </div>
            <div class="bg-white/[0.02] border border-white/[0.04] px-2.5 py-1 rounded-full flex items-center gap-1.5 text-[11px] text-zinc-400">
                <span class="font-medium">Buse</span>
                <span class="text-[9px] text-zinc-600 font-bold uppercase tracking-wider">🔒 Kilitli</span>
            </div>
        </div>

    </div>

</div>
        `;
        container.innerHTML += cardHTML;
    });
}

document.addEventListener('DOMContentLoaded', () => {
    renderMatches();
});
