let lang = "en";

const shellCap = [2, 8, 18, 32];

const elements = [
  { n:1, s:"H", en:"Hydrogen", hu:"Hidrogén", col:1, group:1, period:1, mass:1.008 },
  { n:2, s:"He", en:"Helium", hu:"Hélium", col:18, group:18, period:1, mass:4.0026 },
  { n:6, s:"C", en:"Carbon", hu:"Szén", col:14, group:14, period:2, mass:12.011 },
  { n:8, s:"O", en:"Oxygen", hu:"Oxigén", col:16, group:16, period:2, mass:15.999 },
  { n:26, s:"Fe", en:"Iron", hu:"Vas", col:8, group:8, period:4, mass:55.845 },
  { n:29, s:"Cu", en:"Copper", hu:"Réz", col:11, group:11, period:4, mass:63.546 },
  { n:47, s:"Ag", en:"Silver", hu:"Ezüst", col:11, group:11, period:5, mass:107.8682 },
  { n:79, s:"Au", en:"Gold", hu:"Arany", col:11, group:11, period:6, mass:196.96657 },
  { n:82, s:"Pb", en:"Lead", hu:"Ólom", col:14, group:14, period:6, mass:207.2 },
  { n:92, s:"U", en:"Uranium", hu:"Urán", col:16, group:16, period:7, mass:238.02891 },
  { n:118, s:"Og", en:"Oganesson", hu:"Oganesszon", col:18, group:18, period:7, mass:294 },
  { n:54, s:"Xe", en:"Xenon", hu:"Xenon", col:18, group:18, period:5, mass:131.293 },
  { n:15, s:"P", en:"Phosphorus", hu:"Foszfor", col:15, group:15, period:3, mass:30.973761 },
  { n:20, s:"Ca", en:"Calcium", hu:"Kalcium", col:2, group:2, period:4, mass:40.078 },
  { n:12, s:"Mg", en:"Magnesium", hu:"Magnézium", col:2, group:2, period:3, mass:24.305 },
  { n:26, s:"Fe", en:"Iron", hu:"Vas", col:8, group:8, period:4, mass:55.845 },
  { n:30, s:"Zn", en:"Zinc", hu:"Cink", col:12, group:12, period:4, mass:65.38 },
  { n:53, s:"I", en:"Iodine", hu:"Jód", col:17, group:17, period:5, mass:126.90447 },
  { n:7, s:"N", en:"Nitrogen", hu:"Nitrogén", col:15, group:15, period:2, mass:14.007 },
  { n:16, s:"S", en:"Sulfur", hu:"Kén", col:16, group:16, period:3, mass:32.06 },
  { n:19, s:"K", en:"Potassium", hu:"Kálium", col:1, group:1, period:4, mass:39.0983 },
  { n:25, s:"Mn", en:"Manganese", hu:"Mangán", col:7, group:7, period:4, mass:54.938044 },
  { n:42, s:"Mo", en:"Molybdenum", hu:"Molibdén", col:6, group:6, period:5, mass:95.95 },
  { n:74, s:"W", en:"Tungsten", hu:"Volfrám", col:6, group:6, period:6, mass:183.84 },
  { n:86, s:"Rn", en:"Radon", hu:"Radon", col:18, group:18, period:6, mass:222 },
  { n:10, s:"Ne", en:"Neon", hu:"Neon", col:18, group:18, period:2, mass:20.1797 },
  { n:18, s:"Ar", en:"Argon", hu:"Argon", col:18, group:18, period:3, mass:39.948 },
  { n:34, s:"Se", en:"Selenium", hu:"Szelén", col:16, group:16, period:4, mass:78.971 },
  { n:50, s:"Sn", en:"Tin", hu:"Ón", col:14, group:14, period:5, mass:118.710 },
  { n:78, s:"Pt", en:"Platinum", hu:"Platina", col:10, group:10, period:6, mass:195.084 },
  { n:88, s:"Ra", en:"Radium", hu:"Rádium", col:2, group:2, period:7, mass:226 },
  { n:3, s:"Li", en:"Lithium", hu:"Litium", col:1, group:1, period:2, mass:6.94 },
  { n:4, s:"Be", en:"Beryllium", hu:"Berillium", col:2, group:2, period:2, mass:9.0122 },
  { n:5, s:"B", en:"Boron", hu:"Bór", col:13, group:13, period:2, mass:10.81 },
  { n:9, s:"F", en:"Fluorine", hu:"Fluor", col:17, group:17, period:2, mass:18.998403 },
  { n:11, s:"Na", en:"Sodium", hu:"Nátrium", col:1, group:1, period:3, mass:22.989769 },
  { n:13, s:"Al", en:"Aluminium", hu:"Alumínium", col:13, group:13, period:3, mass:26.981538 },
  { n:14, s:"Si", en:"Silicon", hu:"Szilícium", col:14, group:14, period:3, mass:28.085 },
  { n:17, s:"Cl", en:"Chlorine", hu:"Klór", col:17, group:17, period:3, mass:35.45 },
  { n:21, s:"Sc", en:"Scandium", hu:"Skandium", col:3, group:3, period:4, mass:44.955908 },
  { n:22, s:"Ti", en:"Titanium", hu:"Titán", col:4, group:4, period:4, mass:47.867 },
  { n:23, s:"V", en:"Vanadium", hu:"Vanádium", col:5, group:5, period:4, mass:50.9415 },
  { n:24, s:"Cr", en:"Chromium", hu:"Króm", col:6, group:6, period:4, mass:51.9961 },
  { n:27, s:"Co", en:"Cobalt", hu:"Kobalt", col:9, group:9, period:4, mass:58.933194 },
  { n:28, s:"Ni", en:"Nickel", hu:"Nikkel", col:10, group:10, period:4, mass:58.6934 },
  { n:31, s:"Ga", en:"Gallium", hu:"Gallium", col:13, group:13, period:4, mass:69.723 },
  { n:32, s:"Ge", en:"Germanium", hu:"Germánium", col:14, group:14, period:4, mass:72.63 },
  { n:33, s:"As", en:"Arsenic", hu:"Arzén", col:15, group:15, period:4, mass:74.921595 },
  { n:35, s:"Br", en:"Bromine", hu:"Bróm", col:17, group:17, period:4, mass:79.904 },
  { n:36, s:"Kr", en:"Krypton", hu:"Kripton", col:18, group:18, period:4, mass:83.798 },
  { n:37, s:"Rb", en:"Rubidium", hu:"Rubídium", col:1, group:1, period:5, mass:85.4678 },
  { n:38, s:"Sr", en:"Strontium", hu:"Stroncium", col:2, group:2, period:5, mass:87.62 },
  { n:39, s:"Y", en:"Yttrium", hu:"Itrium", col:3, group:3, period:5, mass:88.90584 },
  { n:40, s:"Zr", en:"Zirconium", hu:"Cirkónium", col:4, group:4, period:5, mass:91.224 },
  { n:41, s:"Nb", en:"Niobium", hu:"Nióbium", col:5, group:5, period:5, mass:92.90637 },
  { n:43, s:"Tc", en:"Technetium", hu:"Teknetium", col:7, group:7, period:5, mass:98 },
  { n:44, s:"Ru", en:"Ruthenium", hu:"Ruthénium", col:8, group:8, period:5, mass:101.07 },
  { n:45, s:"Rh", en:"Rhodium", hu:"Ródium", col:9, group:9, period:5, mass:102.90550 },
  { n:46, s:"Pd", en:"Palladium", hu:"Palládium", col:10, group:10, period:5, mass:106.42 },
  { n:48, s:"Cd", en:"Cadmium", hu:"Kadmium", col:12, group:12, period:5, mass:112.414 },
  { n:49, s:"In", en:"Indium", hu:"Indium", col:13, group:13, period:5, mass:114.818 },
  { n:51, s:"Sb", en:"Antimony", hu:"Antimon", col:15, group:15, period:5, mass:121.760 },
  { n:52, s:"Te", en:"Tellurium", hu:"Tellúr", col:16, group:16, period:5, mass:127.60 },
  { n:55, s:"Cs", en:"Cesium", hu:"Cézium", col:1, group:1, period:6, mass:132.90545196 },
  { n:56, s:"Ba", en:"Barium", hu:"Bárium", col:2, group:2, period:6, mass:137.327 },
  { n:57, s:"La", en:"Lanthanum", hu:"Lantán", col:3, group:3, period:6, mass:138.90547 },
  { n:58, s:"Ce", en:"Cerium", hu:"Cérium", col:4, group:4, period:6, mass:140.116 },
  { n:59, s:"Pr", en:"Praseodymium", hu:"Praseodímium", col:5, group:5, period:6, mass:140.90766 },
  { n:60, s:"Nd", en:"Neodymium", hu:"Neodímium", col:6, group:6, period:6, mass:144.242 },
  { n:61, s:"Pm", en:"Promethium", hu:"Prométium", col:7, group:7, period:6, mass:145 },
  { n:62, s:"Sm", en:"Samarium", hu:"Szamárium", col:8, group:8, period:6, mass:150.36 },
  { n:63, s:"Eu", en:"Europium", hu:"Európium", col:9, group:9, period:6, mass:151.964 },
  { n:64, s:"Gd", en:"Gadolinium", hu:"Gadolínium", col:10, group:10, period:6, mass:157.25 },
  { n:65, s:"Tb", en:"Terbium", hu:"Terbium", col:11, group:11, period:6, mass:158.92535 },
  { n:66, s:"Dy", en:"Dysprosium", hu:"Diszprózium", col:12, group:12, period:6, mass:162.500 },
  { n:67, s:"Ho", en:"Holmium", hu:"Holmium", col:13, group:13, period:6, mass:164.93033 },
  { n:68, s:"Er", en:"Erbium", hu:"Erbium", col:14, group:14, period:6, mass:167.259 },
  { n:69, s:"Tm", en:"Thulium", hu:"Tulium", col:15, group:15, period:6, mass:168.93422 },
  { n:70, s:"Yb", en:"Ytterbium", hu:"Itterbium", col:16, group:16, period:6, mass:173.045 },
  { n:71, s:"Lu", en:"Lutetium", hu:"Lutécium", col:17, group:17, period:6, mass:174.9668 },
  { n:72, s:"Hf", en:"Hafnium", hu:"Hafnium", col:4, group:4, period:6, mass:178.49 },
  { n:73, s:"Ta", en:"Tantalum", hu:"Tantal", col:5, group:5, period:6, mass:180.94788 },
  { n:75, s:"Re", en:"Rhenium", hu:"Rénium", col:7, group:7, period:6, mass:186.207 },
  { n:76, s:"Os", en:"Osmium", hu:"Oszmium", col:8, group:8, period:6, mass:190.23 },
  { n:77, s:"Ir", en:"Iridium", hu:"Irídium", col:9, group:9, period:6, mass:192.217 },
  { n:80, s:"Hg", en:"Mercury", hu:"Higany", col:12, group:12, period:6, mass:200.592 },
  { n:81, s:"Tl", en:"Thallium", hu:"Tallium", col:13, group:13, period:6, mass:204.38 },
  { n:83, s:"Bi", en:"Bismuth", hu:"Bizmut", col:15, group:15, period:6, mass:208.98040 },
  { n:84, s:"Po", en:"Polonium", hu:"Polónium", col:16, group:16, period:6, mass:209 },
  { n:85, s:"At", en:"Astatine", hu:"Asztát", col:17, group:17, period:6, mass:210 },
  { n:87, s:"Fr", en:"Francium", hu:"Francium", col:1, group:1, period:7, mass:223 },
  { n:89, s:"Ac", en:"Actinium", hu:"Aktínium", col:3, group:3, period:7, mass:227 },
  { n:90, s:"Th", en:"Thorium", hu:"Tórium", col:4, group:4, period:7, mass:232.0377 },
  { n:91, s:"Pa", en:"Protactinium", hu:"Protaktínium", col:5, group:5, period:7, mass:231.03588 },
  { n:93, s:"Np", en:"Neptunium", hu:"Neptúnium", col:7, group:7, period:7, mass:237 },
  { n:94, s:"Pu", en:"Plutonium", hu:"Plutónium", col:8, group:8, period:7, mass:244 },
  { n:95, s:"Am", en:"Americium", hu:"Amerícium", col:9, group:9, period:7, mass:243 },
  { n:96, s:"Cm", en:"Curium", hu:"Kürcium", col:10, group:10, period:7, mass:247 },
  { n:97, s:"Bk", en:"Berkelium", hu:"Berkelium", col:11, group:11, period:7, mass:247 },
  { n:98, s:"Cf", en:"Californium", hu:"Kalifornium", col:12, group:12, period:7, mass:251 },
  { n:99, s:"Es", en:"Einsteinium", hu:"Einsteinium", col:13, group:13, period:7, mass:252 },
  { n:100, s:"Fm", en:"Fermium", hu:"Fermium", col:14, group:14, period:7, mass:257 },
  { n:101, s:"Md", en:"Mendelevium", hu:"Mendelevium", col:15, group:15, period:7, mass:258 },
  { n:102, s:"No", en:"Nobelium", hu:"Nobelium", col:16, group:16, period:7, mass:259 },
  { n:103, s:"Lr", en:"Lawrencium", hu:"Lawrencium", col:17, group:17, period:7, mass:262 },
  { n:104, s:"Rf", en:"Rutherfordium", hu:"Rutherfordium", col:4, group:4, period:7, mass:267 },
  { n:105, s:"Db", en:"Dubnium", hu:"Dubnium", col:5, group:5, period:7, mass:270 },
  { n:106, s:"Sg", en:"Seaborgium", hu:"Seaborgium", col:6, group:6, period:7, mass:271 },
  { n:107, s:"Bh", en:"Bohrium", hu:"Bórium", col:7, group:7, period:7, mass:270 },
  { n:108, s:"Hs", en:"Hassium", hu:"Hássium", col:8, group:8, period:7, mass:277 },
  { n:109, s:"Mt", en:"Meitnerium", hu:"Meitnérium", col:9, group:9, period:7, mass:276 },
  { n:110, s:"Ds", en:"Darmstadtium", hu:"Darmstadtium", col:10, group:10, period:7, mass:281 },
  { n:111, s:"Rg", en:"Roentgenium", hu:"Röntgenium", col:11, group:11, period:7, mass:282 },
  { n:112, s:"Cn", en:"Copernicium", hu:"Kopernícium", col:12, group:12, period:7, mass:285 },
  { n:113, s:"Nh", en:"Nihonium", hu:"Nihónium", col:13, group:13, period:7, mass:286 },
  { n:114, s:"Fl", en:"Flerovium", hu:"Flerovium", col:14, group:14, period:7, mass:289 },
  { n:115, s:"Mc", en:"Moscovium", hu:"Moszkóvium", col:15, group:15, period:7, mass:288 },
  { n:116, s:"Lv", en:"Livermorium", hu:"Livermorium", col:16, group:16, period:7, mass:293 },
  { n:117, s:"Ts", en:"Tennessine", hu:"Tennessine", col:17, group:17, period:7, mass:294 },
];

const table = document.getElementById("table");
const svg = document.getElementById("atomSvg");

function electronShells(Z) {
  let remaining = Z;
  let shells = [];
  for (let cap of shellCap) {
    if (remaining <= 0) break;
    let used = Math.min(cap, remaining);
    shells.push(used);
    remaining -= used;
  }
  return shells;
}

function renderAtom(e) {
  const svg = document.getElementById("atomSvg");
  svg.innerHTML = "";

  const cx = 130, cy = 130;
  const neutrons = Math.round(e.mass - e.n);
  const shellCaps = [2, 8, 18, 32];

  // 🔴 atommag (outline)
  svg.innerHTML += `
    <circle cx="${cx}" cy="${cy}" r="20" class="nucleus"/>
    <text x="${cx}" y="${cy - 2}" text-anchor="middle">p: ${e.n}</text>
    <text x="${cx}" y="${cy + 10}" text-anchor="middle">n: ${neutrons}</text>
  `;

  let remaining = e.n;
  let shellIndex = 0;

  while (remaining > 0) {
    const cap = shellCaps[shellIndex];
    const count = Math.min(cap, remaining);
    const radius = 45 + shellIndex * 28;
    const speed = 8 + shellIndex * 4;

    // ⚪ pálya
    svg.innerHTML += `
      <circle cx="${cx}" cy="${cy}" r="${radius}" class="orbit"/>
    `;

    // 🔵 forgó héj csoport
    const shellGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
    shellGroup.style.transformOrigin = `${cx}px ${cy}px`;
    shellGroup.style.animation = `spin ${speed}s linear infinite`;

    for (let i = 0; i < count; i++) {
      const angle = (2 * Math.PI / count) * i;
      const ex = cx + Math.cos(angle) * radius;
      const ey = cy + Math.sin(angle) * radius;

      const electron = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      electron.setAttribute("cx", ex);
      electron.setAttribute("cy", ey);
      electron.setAttribute("r", 4);
      electron.setAttribute("class", "electron");

      shellGroup.appendChild(electron);
    }

    svg.appendChild(shellGroup);

    remaining -= count;
    shellIndex++;
  }
}

function renderTable() {
  table.innerHTML = "";
  elements.forEach(e => {
    const d = document.createElement("div");
    d.className = "element";
    d.style.gridColumn = e.col;
    d.style.gridRow = e.period;

    d.innerHTML = `
      <div class="number">${e.n}</div>
      <div class="symbol">${e.s}</div>
    `;

    d.onclick = () => {
      const name = lang === "en" ? e.en : e.hu;
      document.getElementById("name").innerText =
        `${name} (${e.s})`;

      document.getElementById("details").innerText =
        lang === "en"
          ? `Atomic number: ${e.n}
Period: ${e.period}
Group: ${e.group}`
          : `Rendszám: ${e.n}
Periódus: ${e.period}
Csoport: ${e.group}`;

      renderAtom(e);
    };

    table.appendChild(d);
  });
}

window.toggleLang = () => {
  lang = lang === "en" ? "hu" : "en";
};

renderTable();
