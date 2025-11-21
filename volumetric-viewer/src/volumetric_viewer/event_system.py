from queue import Empty, Queue


class Event:
    pass

class NHDRLoadedEvent(Event):
    def __init__(self, filepath: str):
        self.filepath = filepath

    def __repr__(self):
        return f"<NHDRLoadedEvent filepath={self.filepath}>"
    
class RawLoadedEvent(Event):
    def __init__(self, filepath: str):
        self.filepath = filepath

    def __repr__(self):
        return f"<RawLoadedEvent filepath={self.filepath}>"

class ColorChangedEvent(Event):
    def __init__(self, color: tuple[int, int, int]):
        self.color = color

    def __repr__(self):
        return f"<ColorChangedEvent color={self.color}>"

class MinIsovalueChangedEvent(Event):
    def __init__(self, isovalue: int):
        self.isovalue = isovalue

    def __repr__(self):
        return f"<MinIsovalueChangedEvent isovalue={self.isovalue}>"
    
class MaxIsovalueChangedEvent(Event):
    def __init__(self, isovalue: int):
        self.isovalue = isovalue

    def __repr__(self):
        return f"<MaxIsovalueChangedEvent isovalue={self.isovalue}>"
    
class ViewModeChangedEvent(Event):
    def __init__(self, view_mode: int):
        self.view_mode = view_mode

    def __repr__(self):
        return f"<ViewModeChangedEvent view_mode={self.view_mode}>"
    
class TransferFunctionImportedEvent(Event):
    def __init__(self, filepath: str):
        self.filepath = filepath

    def __repr__(self):
        return f"<TransferFunctionImportedEvent filepath={self.filepath}>"

class TransferFunctionExportedEvent(Event):
    def __init__(self, filepath: str):
        self.filepath = filepath

    def __repr__(self):
        return f"<TransferFunctionExportedEvent filepath={self.filepath}>"
    
class TransferFunctionUpdateEvent(Event):
    def __init__(self, data: dict):
        self.data = data

    def __repr__(self):
        return f"<TransferFunctionUpdatedEvent filepath={self.data}>"

class EventQueue:
    def __init__(self):
        self._queue = Queue()

    def push(self, event: Event):
        self._queue.put(event)

    def pop_all(self):
        events = []
        while True:
            try:
                events.append(self._queue.get_nowait())
            except Empty:
                break
        return events
