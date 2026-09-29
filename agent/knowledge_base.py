"""
knowledge_base.py — Physics KB for PhysicsBuddy Agent
12 documents, each covering ONE specific topic, 100-500 words each.
Loaded and verified via ChromaDB BEFORE graph assembly.
"""

PHYSICS_DOCUMENTS = [
    {
        "id": "doc_001",
        "topic": "Newton's Laws of Motion",
        "text": (
            "Newton's Laws of Motion are the three foundational principles that describe how objects move. "
            "The First Law (Law of Inertia) states that an object at rest stays at rest and an object in motion "
            "stays in motion with the same speed and direction unless acted upon by an unbalanced external force. "
            "This explains why passengers jerk forward when a bus brakes suddenly. "
            "The Second Law states that Force equals mass times acceleration (F = ma). This means a larger force "
            "produces greater acceleration, and a heavier object requires more force to achieve the same acceleration. "
            "For example, pushing a 2 kg box with 10 N produces 5 m/s² acceleration. "
            "The Third Law states that for every action there is an equal and opposite reaction. "
            "When you push a wall with 50 N, the wall pushes back on you with 50 N. "
            "Rockets work on this principle: exhaust gases are expelled downward, pushing the rocket upward. "
            "Common exam questions involve finding net force, calculating acceleration given mass and force, "
            "and identifying action-reaction pairs. Always draw a free-body diagram before applying F = ma."
        )
    },
    {
        "id": "doc_002",
        "topic": "Kinematics — Equations of Motion",
        "text": (
            "Kinematics describes the motion of objects without considering the forces that cause motion. "
            "The four standard equations of motion for uniform acceleration are: "
            "(1) v = u + at, where u is initial velocity, v is final velocity, a is acceleration, t is time. "
            "(2) s = ut + ½at², where s is displacement. "
            "(3) v² = u² + 2as. "
            "(4) s = (u + v)/2 × t. "
            "These equations only apply when acceleration is constant. "
            "For a freely falling body, acceleration a = g = 9.8 m/s² downward. "
            "For a body thrown upward, at the highest point velocity v = 0 and then it falls back. "
            "Projectile motion combines horizontal motion (constant velocity, no acceleration) and "
            "vertical motion (constant acceleration due to gravity). "
            "The horizontal range R = u²sin(2θ)/g, maximum height H = u²sin²(θ)/2g, "
            "and time of flight T = 2u·sinθ/g, where θ is the angle of projection. "
            "A common mistake is applying these equations when acceleration is not constant — "
            "in such cases, use calculus or graphs."
        )
    },
    {
        "id": "doc_003",
        "topic": "Work, Energy, and Power",
        "text": (
            "Work is done when a force causes displacement. W = F·d·cosθ, where θ is the angle between "
            "force and displacement. Work is a scalar quantity measured in Joules (J). "
            "If force is perpendicular to displacement (θ = 90°), no work is done — example: a porter carrying "
            "a bag on his head while walking horizontally does zero work against gravity. "
            "Kinetic Energy (KE) = ½mv² is the energy of motion. "
            "Potential Energy (PE) = mgh is stored energy due to position. "
            "The Work-Energy Theorem states: Net work done = Change in KE. "
            "Conservation of Energy: Total mechanical energy (KE + PE) is constant in the absence of non-conservative forces. "
            "Power is the rate of doing work: P = W/t = F·v, measured in Watts (W). "
            "1 horsepower = 746 W. "
            "Efficiency = (Useful Output / Total Input) × 100%. "
            "Common problem types: finding velocity using energy conservation, comparing power of engines, "
            "and calculating work done against friction."
        )
    },
    {
        "id": "doc_004",
        "topic": "Laws of Thermodynamics",
        "text": (
            "Thermodynamics deals with heat, work, and temperature, and their relation to energy. "
            "Zeroth Law: If two systems are each in thermal equilibrium with a third system, they are in "
            "thermal equilibrium with each other. This defines temperature. "
            "First Law (Conservation of Energy): ΔU = Q - W, where ΔU is change in internal energy, "
            "Q is heat added to the system, W is work done by the system. "
            "For an isothermal process (constant T): ΔU = 0, so Q = W. "
            "For an adiabatic process (Q = 0): ΔU = -W. "
            "Second Law: Heat cannot spontaneously flow from a cold body to a hot body. "
            "Entropy of an isolated system never decreases. "
            "Carnot efficiency η = 1 - T_cold/T_hot (temperatures in Kelvin). "
            "Third Law: As temperature approaches absolute zero, entropy approaches a constant minimum. "
            "Key concepts for exams: identifying the type of thermodynamic process from PV diagrams, "
            "calculating efficiency of heat engines, and applying the First Law to open/closed systems."
        )
    },
    {
        "id": "doc_005",
        "topic": "Electrostatics — Coulomb's Law and Electric Field",
        "text": (
            "Electrostatics is the study of electric charges at rest. "
            "Coulomb's Law: The force between two point charges is F = kq₁q₂/r², where k = 9×10⁹ N·m²/C², "
            "q₁ and q₂ are the charges in Coulombs, and r is the distance between them. "
            "Like charges repel, unlike charges attract. Force is along the line joining the charges. "
            "Electric Field E at a point is the force per unit positive charge: E = F/q = kQ/r². "
            "Electric field lines originate from positive charges and terminate at negative charges. "
            "They never intersect. Closer lines mean stronger field. "
            "Gauss's Law: The total electric flux through a closed surface = Q_enclosed / ε₀. "
            "This is used to find E for symmetric charge distributions (sphere, cylinder, plane). "
            "Electric Potential V = kQ/r. It is a scalar quantity. "
            "Relation between field and potential: E = -dV/dr. "
            "Potential energy of a charge q in potential V: U = qV. "
            "Common mistakes: confusing field (vector) with potential (scalar), "
            "and forgetting to check for superposition when multiple charges are present."
        )
    },
    {
        "id": "doc_006",
        "topic": "Current Electricity — Ohm's Law and Circuits",
        "text": (
            "Current electricity deals with charges in motion. "
            "Electric current I = Q/t, measured in Amperes (A). "
            "Ohm's Law: V = IR, where V is voltage in Volts, I is current in Amperes, R is resistance in Ohms. "
            "Resistance R = ρL/A, where ρ is resistivity, L is length, A is cross-sectional area. "
            "Resistivity increases with temperature for conductors and decreases for semiconductors. "
            "Series circuits: same current, resistances add (R_total = R1 + R2 + ...). "
            "Parallel circuits: same voltage, reciprocal resistances add (1/R_total = 1/R1 + 1/R2 + ...). "
            "Kirchhoff's Current Law (KCL): Sum of currents entering a node = Sum leaving it. "
            "Kirchhoff's Voltage Law (KVL): Sum of EMFs = Sum of voltage drops in a closed loop. "
            "Power dissipated: P = VI = I²R = V²/R. "
            "A cell of EMF ε and internal resistance r: terminal voltage = ε - Ir. "
            "Exam tip: For complex circuits, first simplify parallel and series combinations, then apply Kirchhoff's laws."
        )
    },
    {
        "id": "doc_007",
        "topic": "Waves and Sound",
        "text": (
            "A wave is a disturbance that transfers energy without transferring matter. "
            "Transverse waves: oscillations perpendicular to direction of propagation (light, string waves). "
            "Longitudinal waves: oscillations parallel to direction of propagation (sound). "
            "Key quantities: Amplitude (A), Wavelength (λ), Frequency (f), Period (T = 1/f), Speed (v = fλ). "
            "Speed of sound in air at 0°C ≈ 332 m/s; increases with temperature. "
            "The Doppler Effect: apparent change in frequency when source or observer moves. "
            "f_observed = f_source × (v ± v_observer)/(v ∓ v_source). "
            "When source approaches observer, frequency increases (higher pitch). "
            "Standing waves form when two identical waves travel in opposite directions. "
            "Nodes (zero amplitude) and antinodes (maximum amplitude) form. "
            "For a string of length L: λ_n = 2L/n, f_n = nv/2L (harmonics). "
            "Resonance: maximum energy transfer when driving frequency equals natural frequency. "
            "Decibel level: β = 10 log₁₀(I/I₀), where I₀ = 10⁻¹² W/m² is threshold of hearing. "
            "Exam focus: Doppler effect numericals, harmonic frequency calculations, and standing wave patterns."
        )
    },
    {
        "id": "doc_008",
        "topic": "Optics — Reflection and Refraction",
        "text": (
            "Optics studies the behaviour of light. "
            "Law of Reflection: Angle of incidence = Angle of reflection (measured from the normal). "
            "Mirror formula: 1/f = 1/v + 1/u, where f is focal length, v is image distance, u is object distance. "
            "Sign convention: distances measured from the pole; real distances are negative (for mirrors). "
            "Magnification m = -v/u. Negative m means inverted image. "
            "Refraction: light bends when it passes from one medium to another. "
            "Snell's Law: n₁ sinθ₁ = n₂ sinθ₂. "
            "Refractive index n = c/v_medium = speed of light in vacuum / speed in medium. "
            "Total Internal Reflection (TIR) occurs when light travels from denser to rarer medium "
            "and angle of incidence exceeds critical angle (sinθ_c = n₂/n₁). "
            "TIR is used in optical fibres. "
            "Lens formula: 1/f = 1/v - 1/u. Power of lens P = 1/f (in metres), unit is Dioptre. "
            "Prism disperses white light into a spectrum (VIBGYOR). "
            "Exam tips: Always apply sign convention carefully; draw ray diagrams for image location."
        )
    },
    {
        "id": "doc_009",
        "topic": "Gravitation — Newton's Law and Orbital Motion",
        "text": (
            "Newton's Law of Universal Gravitation: Every mass attracts every other mass. "
            "F = Gm₁m₂/r², where G = 6.674×10⁻¹¹ N·m²/kg² is the gravitational constant. "
            "Acceleration due to gravity on Earth's surface g = GM_E/R_E² ≈ 9.8 m/s². "
            "g decreases with height: g_h = g(1 - 2h/R_E) for h << R_E. "
            "g decreases inside Earth: g_d = g(1 - d/R_E). "
            "Gravitational Potential Energy U = -GMm/r (negative because gravity is attractive). "
            "Escape velocity: v_e = √(2GM/R) = √(2gR) ≈ 11.2 km/s for Earth. "
            "Orbital velocity for circular orbit: v_o = √(GM/r) = √(gR²/r). "
            "At surface orbit: v_o ≈ 7.9 km/s. "
            "Kepler's Laws: (1) Planets move in ellipses with Sun at one focus. "
            "(2) Equal areas are swept in equal times (conservation of angular momentum). "
            "(3) T² ∝ r³ — the square of orbital period is proportional to the cube of semi-major axis. "
            "Geostationary satellites orbit at ~36,000 km with T = 24 hours. "
            "Weightlessness in orbit: both satellite and astronaut have same free-fall acceleration — "
            "normal force becomes zero, producing apparent weightlessness."
        )
    },
    {
        "id": "doc_010",
        "topic": "Modern Physics — Photoelectric Effect and Quantum Basics",
        "text": (
            "The Photoelectric Effect is the emission of electrons from a metal surface when light falls on it. "
            "Einstein explained it using quanta of light called photons. "
            "Energy of a photon: E = hf = hc/λ, where h = 6.626×10⁻³⁴ J·s is Planck's constant. "
            "Threshold frequency f₀: minimum frequency required for emission. "
            "Work function φ = hf₀ is the minimum energy needed to eject an electron. "
            "Kinetic energy of ejected electron: KE_max = hf - φ = h(f - f₀). "
            "Stopping potential V₀: voltage needed to stop the fastest electrons. eV₀ = KE_max. "
            "Key facts: Intensity increases number of electrons but NOT their KE. "
            "Only frequency determines whether emission occurs. "
            "de Broglie Wavelength: λ = h/mv = h/p. Every particle has a wave nature. "
            "Bohr's Model of Hydrogen Atom: electrons orbit in fixed energy levels. "
            "Energy of nth level: E_n = -13.6/n² eV. "
            "When electron jumps from higher to lower level, photon is emitted with energy = ΔE. "
            "Heisenberg's Uncertainty Principle: Δx·Δp ≥ h/4π — position and momentum cannot both be "
            "known precisely simultaneously. This is a fundamental quantum limit, not a measurement error."
        )
    },
    {
        "id": "doc_011",
        "topic": "Rotational Motion and Moment of Inertia",
        "text": (
            "Rotational motion is the analog of linear motion but for objects rotating about an axis. "
            "Angular displacement θ (radians), angular velocity ω (rad/s), angular acceleration α (rad/s²). "
            "Relation to linear quantities: v = rω, a_tangential = rα, a_centripetal = rω² = v²/r. "
            "Rotational analog of Newton's second law: τ = Iα, where τ is torque and I is moment of inertia. "
            "Torque τ = r × F = rF sinθ (measures how effectively a force causes rotation). "
            "Moment of Inertia I = Σmr² (distribution of mass about the axis). "
            "For common shapes: Solid sphere: I = 2mr²/5; Hollow sphere: 2mr²/3; "
            "Solid cylinder: mr²/2; Thin ring: mr². "
            "Parallel Axis Theorem: I = I_cm + md², where d is distance between axes. "
            "Angular momentum L = Iω. Conservation of angular momentum: if no external torque, L is constant. "
            "Example: a spinning figure skater pulls arms in, reducing I, so ω increases to conserve L. "
            "Rolling without slipping: v_cm = rω. KE_total = ½mv² + ½Iω². "
            "Exam tip: Always identify whether the object is rotating, rolling, or both before selecting equations."
        )
    },
    {
        "id": "doc_012",
        "topic": "Magnetism — Magnetic Force and Electromagnetic Induction",
        "text": (
            "A moving charge in a magnetic field experiences a force: F = qv × B = qvB sinθ. "
            "This is the Lorentz force. It is always perpendicular to velocity, so it does no work. "
            "A charged particle in a uniform magnetic field moves in a circle: r = mv/qB. "
            "Force on a current-carrying conductor: F = IL × B = BIL sinθ. "
            "Biot-Savart Law: dB = (μ₀/4π)(IdL × r̂/r²). Magnetic field at centre of circular loop: B = μ₀I/2R. "
            "Ampere's Law: ∮B·dL = μ₀I_enclosed — used for symmetric current distributions. "
            "Field inside a solenoid: B = μ₀nI, where n is number of turns per unit length. "
            "Electromagnetic Induction (Faraday's Law): EMF = -dΦ/dt, where Φ = B·A·cosθ is magnetic flux. "
            "Lenz's Law: Induced current opposes the change that caused it (conservation of energy). "
            "Motional EMF: ε = BLv, for a conductor of length L moving at speed v perpendicular to field B. "
            "Self-inductance L: EMF = -L(dI/dt). Energy stored in inductor: U = ½LI². "
            "Transformer equation: V₁/V₂ = N₁/N₂ = I₂/I₁. "
            "Exam focus: Lenz's law problems, motional EMF, and transformer calculations."
        )
    }
]
