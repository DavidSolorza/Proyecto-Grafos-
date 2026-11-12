"""Commands of a running match: buy, choose soldiers, order transport, consult routes, advance the clock."""

FINISHED = ("VICTORY_ELIMINATION", "VICTORY_RESISTANCE", "DEFEAT")
FREE = ("AT_BASE", "STATIONED")        # soldiers that can receive orders


class MatchCommands:
    """Mixed into Store: every method calls the Flask API and keeps the returned snapshot in `self.sim`."""

    def _apply(self, res) -> bool:
        if not res:
            return False
        self.sim = res["state"]
        if self.finished:
            self.running = False
        return True

    def recruit(self, kind: str) -> None:
        if self._apply(self._try(self.api.recruit, kind, 1)):
            self._remember()

    def toggle_pick(self, soldier_id: str) -> None:
        soldier = next((s for s in self.sim["soldiers"] if s["id"] == soldier_id), None)
        if soldier is None or soldier["status"] not in FREE:
            return
        self.route_text = ""
        self.picked = [p for p in self.picked if p != soldier_id] if soldier_id in self.picked else self.picked + [soldier_id]

    def send(self) -> None:
        if not self.picked or not self.dest:
            return
        if self.mode == "air":
            res = self._try(self.api.fly, self.picked, self.dest)
        else:
            res = self._try(self.api.move, self.picked, self.dest, self.mode)
        if self._apply(res):
            self.picked, self.route_text = [], ""
            self._remember()

    def show_route(self) -> None:
        first = next((s for s in self.sim["soldiers"] if s["id"] == (self.picked or [None])[0]), None)
        if first is None or not self.dest or self.mode == "air":
            return
        res = self._try(self.api.path, first["vertex"], self.dest, "moto" if self.mode == "moto" else "walk")
        if res:
            path = res.get("path")
            self.route_text = f"{' > '.join(path['vertices'])} ({path['time']}s)" if path else "Sin ruta disponible"

    def advance(self, seconds: float) -> None:
        self._apply(self._try(self.api.tick, seconds))

    def toggle_play(self) -> None:
        if self.sim is None or self.finished:
            return
        self.running = not self.running
        self._last_tick = self.now
        if not self.running:
            self._remember()
