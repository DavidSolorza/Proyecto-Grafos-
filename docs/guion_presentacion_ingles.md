# TECHNICAL PRESENTATION SCRIPT IN ENGLISH (SECOND LANGUAGE REQUIREMENT)
## "The Defeat of Dictator General P. Tardo: Data Structures & Algorithmic Design"
**Format:** Academic Video Presentation / Technical Walkthrough  
**Language:** English (Professional / Academic Tone)  
**Estimated Duration:** 10 to 12 minutes  
**Target Audience:** Evaluation Committee & Course Professors  
**Participants:** All team members contributing equally  

---

## 🎯 OBJECTIVE & STATEMENT COMPLIANCE
Fulfill Section 14 of the official assignment specification: *"Video de explicación de solución en una segunda lengua, estructuras y algoritmos, con participación de todos los integrantes"*.  
The script provides a rigorous explanation of domain modeling, spatial graph representations, computational complexity, Kruskal's MST, Greedy optimization, Dijkstra's algorithm with dynamic risk weights, and event-driven simulation consistency.

---

## 👥 ROLES & PRESENTATION OUTLINE

```
[Speaker 1: Project Lead & Architecture]      00:00 - 02:15  |  Introduction, Problem Domain & Graph Representations
[Speaker 2: Algorithmic Specialist]          02:15 - 04:45  |  MST Construction & Greedy Tower Allocation Formula
[Speaker 3: Systems & Combat Engineer]        04:45 - 07:15  |  Ballistic Models, AOE Combat & Reactive Convoy Rerouting
[Speaker 4: Logistics & Verification Lead]    07:15 - 09:30  |  Dynamic Infrastructure, Aerial Redistribution & Invariants
[All Speakers / Joint Closing]                09:30 - 11:00  |  Complexity Analysis, Test Coverage & Final Conclusions
```

---

## 🎙️ FULL DETAILED SCRIPT

### PART 1: INTRODUCTION & DUAL GRAPH REPRESENTATION (00:00 - 02:15)
- **Speaker 1 (Project Lead):**
  > *"Good morning, esteemed professors and colleagues. Today, our team is proud to present our solution for the Data Structures term project: 'The Defeat of Dictator General P. Tardo'.*  
  > *The core challenge of this project lies in modeling two independent networks that share the same Cartesian coordinate plane without any cross-edges connecting them.*  
  > *First, we have the Elevated Graph, denoted as $G_E$. This network represents the high-altitude defensive infrastructure used by human soldiers. Its vertices feature three-dimensional elevation ($z \ge 0$), containing exactly one Command Base, candidate defensive towers, transit waypoints, and strategic heliports. Its edges represent walkways and vehicular bridges with discrete structural health points.*  
  > *Second, we have the Labyrinth Graph, denoted as $G_M$. This is the subterranean network through which the enemy autonomous convoy advances from a unique entry point to a designated exit.*  
  > *As mandated by Section 2 of the specification, we have implemented all graph representations and auxiliary structures from scratch. We strictly avoided third-party graph packages like NetworkX or graph-tool, and implemented our own custom priority queues without using Python's standard `heapq` module."*

---

### PART 2: MINIMUM SPANNING TREE & GREEDY TOWER OPTIMIZATION (02:15 - 04:45)
- **Speaker 2 (Algorithmic Specialist):**
  > *"Let us delve into Phase 1: Pre-combat Defensive Planning.*  
  > *Before any battle begins, our system must solve a strategic optimization problem. To ensure logistical reachability, we first execute Kruskal's algorithm over the connected component of $G_E$ containing the base, using pedestrian walking time as edge weights.*  
  > *Our Kruskal implementation is backed by a custom Disjoint-Set structure with path compression and union by rank, achieving a quasi-linear time complexity of $\mathcal{O}(E \log E)$. The resulting tree, $T_E$, serves as an immutable reference of connectivity without pruning the remaining edges of the graph.*  
  > *Next, we address the tower selection problem using a greedy heuristic. In each round, we evaluate all accessible candidate positions using the official score formula:*  
  > $$S(p) = \frac{C(p)}{1 + \frac{D_T(B, p)}{D_0}}$$  
  > *Here, $C(p)$ represents the sum of lengths of currently unmonitored labyrinth corridors whose horizontal midpoint falls within the tower's surveillance radius $R_v$. The denominator penalizes logistical delay: $D_T(B, p)$ is the shortest path travel time from the base to candidate $p$ strictly following tree $T_E$, normalized by the configurable benchmark time $D_0$.*  
  > *The candidate maximizing $S(p)$ is chosen, coverage is updated, and the process repeats until either $K$ towers are placed or no remaining candidate provides new coverage. Ties are deterministically resolved by smaller tree distance and lexicographical identifier."*

---

### PART 3: BALLISTIC COMBAT & CONVOY REACTIVE NAVIGATION (04:45 - 07:15)
- **Speaker 3 (Systems & Combat Engineer):**
  > *"Once defenses are established, Phase 2 commences under a discrete logical clock advancing in intervals of $\Delta t = 0.25$ seconds.*  
  > *Each tower accommodates at most three soldiers. We model three specialized units: Infantry, Snipers, and Heavy Gunners.*  
  > *A key requirement of Section 5 is the ballistic range elevation formula:*  
  > $$R_{\text{eff}} = R_{\text{base}} \cdot (1 + \beta \cdot z)$$  
  > *Towers with higher $z$-coordinates grant a substantial tactical reach advantage. When firing, Infantry and Snipers prioritize the living enemy unit with the lowest current health to maximize elimination rates, whereas Gunners inflict Area of Effect (AOE) damage across all living targets within range.*  
  > *Concurrently, the enemy convoy exhibits dynamic reactive navigation. Rather than following a static path, at every labyrinth intersection the convoy re-evaluates edge costs according to active defense threats:*  
  > $$w(e) = t(e) + \alpha \cdot P(e)$$  
  > *Damage potential $P(e)$ is computed by sampling damage rates $D(q)$ at the start, midpoint, and end of corridor $e$. Using a custom Dijkstra algorithm with our `MinHeap`, the convoy chooses the path minimizing total perceived cost, incorporating intelligent turnback prevention to avoid trivial oscillations unless trapped."*

---

### PART 4: DYNAMIC BRIDGES, LOGISTICS & INVARIANTS (07:15 - 09:30)
- **Speaker 4 (Logistics & Verification Lead):**
  > *"In Section 8, the physical infrastructure itself is subjected to wear and tear. Foot patrols do not degrade bridges, but every motorcycle crossing decrements bridge resistance by exactly one health point:*  
  > $$\text{HP}_{\text{current}} \leftarrow \text{HP}_{\text{current}} - 1$$  
  > *When resistance drops to zero, the bridge collapses immediately. Ongoing crossings are allowed to finish, but no new transfers may enter. A background repair crew is dispatched, rebuilding the bridge after a configurable countdown.*  
  > *For rapid troop deployment, Section 9 introduces tactical helicopter flights carrying up to four soldiers. If the target tower is full upon arrival, our surplus distribution algorithm automatically redirects remaining soldiers to the nearest enabled tower based on Euclidean distance, returning to base only if all towers are saturated.*  
  > *Throughout the entire simulation, our state engine enforces strict domain invariants: financial balances never drop below zero, capacity limits of three soldiers per tower are strictly conserved, and logical clock ticks maintain deterministic ordering between combat resolution, exit checks, and timeout events."*

---

### PART 5: COMPLEXITY ANALYSIS & CONCLUSIONS (09:30 - 11:00)
- **Speaker 1 (Closing on behalf of the team):**
  > *"To conclude, let us review our computational complexity benchmarks:*  
  > *- Graph Representation: $\mathcal{O}(V + E)$ spatial footprint via adjacency lists.*  
  > *- MST Construction: $\mathcal{O}(E \log V)$ with custom Union-Find.*  
  > *- Priority Queue Operations: $\mathcal{O}(\log V)$ insertion and extraction via custom binary min-heaps.*  
  > *- Simulation Step: $\mathcal{O}(S + C)$ per 0.25s logical tick, where $S$ is active soldiers and $C$ is convoy size.*  
  > *Our dual-client architecture—featuring a 100% procedural vector Pygame desktop client and a responsive React web interface—communicates seamlessly with the Python core engine.*  
  > *With 232 backend unit tests, 91 Pygame desktop tests, and 47/47 audit points passing with 100% success rate, our system proves that rigorous software engineering and theoretical computer science can merge into a robust, high-performance simulation.*  
  > *Thank you very much for your time and evaluation."*
