
import time
import json
import os
import tempfile
import shutil
import datetime

from enum import unique, Enum

from services.base_svc import BaseService
import config


MISSING_PARAM = object()


class TrackerSvc(BaseService):
    """Record tracking base version. Tracks and displays to Standard out."""

    @unique
    class Record(Enum):
        DEFERRED = "Deferred"
        INFO = "Info"
        SNAP = "Snap"
        TEARDOWN = "+Teardown"

        POLL_START = "Poll Start"
        POLL_END = "Poll End"

        PASS = "Pass"
        FAIL = "FAIL"

        START_AT = "Start At"
        NEW_PAGE = "New Page"
        NEW_FORM = "+New Form"
        REFRESH_PAGE = "+Refresh Page"

        # do action - poke
        CLICK = "+Click"
        CLEAR = "+Clear"
        TYPE_INTO = "+Type into"
        SUBMIT_FORM = "+Submit form"
        CLICK_ONE_OF_OPTIONS = "Click One Of Options"
        CLICK_ONE_OF_OPTIONS_BY_SUBSTRING = "+Click One Of Options By Substring"
        CLICK_ONE_OF_CLICK = "+Click One Of Click"
        CLICK_ONE_OF_BY_INDEX_OPTIONS = "Click One Of By Index Options"
        CLICK_ONE_OF_BY_INDEX_CLICK = "+Click One Of By Index Click"
        FIND_ONE_OF_BY_INDEX = "Find One Of By Index"
        START_WITH = "Start With"
        JUST_FIND_IT = "Just Find It"
        MOVE_TO = "Move to"
        MOVE_AND_CLICK = "+Move to and Click"
        SELECT_THE = "Select The"
        SELECT_FROM = "Select From"

        SET_COOKIE = "Set Cookie"
        GET_COOKIE = "Get Cookie"

        # just looking - peek
        VERIFY = "+Verify"

        IS_THIS_DISPLAYED = "Is this displayed"
        IS_THIS_ENABLED = "Is This Enabled"
        IS_THIS_SELECTED = "Is This Selected"
        THE_TEXT = "The text"
        THE_TEXT_STRIPPED = "The text stripped"
        THE_TEXT_LOWER = "The text lower"
        ALL_THE_TEXT = "All the text"
        ALL_THE_TEXT_LOWER = "All the text lower"
        THE_ATTRIBUTE = "The Attribute"
        ALL_THE_ATTRIBUTES = "All The Attributes"
        INT_OF = "Int of"
        ALL_INTS_OF = "All Ints of"
        INT_OF_REGEX = "Int of regex"
        ALL_INTS_OF_REGEX = "All Ints of regex"
        INT_OF_ATTRIBUTE = "Int of Attribute"
        LENGTH_OF = "Length of"
        LENGTH_OF_DISPLAYED = "Length of Displayed"
        Y_POSITION = "Y Position"

        CAN_FIND_THE = "Can Find The"
        SHOULD_NOT_FIND_THE = "Should Not Find The"

        ATTRIBUTE_CLASS = "Attribute class"
        ATTRIBUTE_CLASS_VALUE = "Attribute class value"
        ATTRIBUTE_FUNC = "Attribute func"
        ATTRIBUTE_FUNC_VALUE = "Attribute func value"


    FILTER_INIT_CHARS = "+"
    FILTER_EVENT_TYPES = [Record.SNAP, ]

    def __init__(self, auto, recorder_svc, writers, additions, subtractions):
        BaseService.__init__(self)
#        self.records = []
        self.page_id = -1
        self.snaps = 0
        self.auto = auto
        self.recorder_svc = recorder_svc
# TODO where does this go?
#        self.test_pass_start_time = None
#        self.tst_name = self.auto.find_automation_complete_name()
#        if len(self.auto.find_automation_complete_name()) > TrackerSvc.MAX_TST_NAME_LENGTH:
#            self.tst_name = self.auto.find_automation_complete_name()[:TrackerSvc.MAX_TST_NAME_LENGTH] + '...'
#        self.test_run_id =  'TODO'  #  None

        writers.extend(additions)
        self.writers = [w(self) for w in writers if w not in subtractions]

    #    self.username = self.auto.env.get_username()

    def teardown(self):
        try:
            self.output_all_records()
        except Exception as e:
            print e
            return self.ERRORS_IN_TEARDOWN

        return self.SUCCESSFUL_TEARDOWN

    def track(self, record_type, message, value=MISSING_PARAM, location=MISSING_PARAM):
        for writer in self.writers:
            writer.do_track(record_type, message, value, location)

    def track_all(self, record_type, message, values=(), locations=()):
        for writer in self.writers:
            writer.do_track_all(record_type, message, values, locations)

    def on_new_page(self):
        self.page_id += 1
        for writer in self.writers:
            writer.do_on_new_page()

    def add_snap(self):
        self.snaps += 1
        for writer in self.writers:
            writer.do_add_snap()

    def _get_snap_count(self):
        return self.snaps

    snap_count = property(_get_snap_count)

    def output_all_records(self):
        for writer in self.writers:
            writer.do_output_all_records()


class WriterBase(object):
    def __init__(self, tracker):
        self.tracker = tracker


    def do_track(self, record_type, message, value=MISSING_PARAM, location=MISSING_PARAM):
        """Tracks a record."""
        if value == MISSING_PARAM:
            values = []
        else:
            values = [value,]
        if location == MISSING_PARAM:
            locations = []
        else:
            locations = [location,]
        self.do_track_all(record_type, message, values=values, locations=locations)

    def do_track_all(self, record_type, message, values=(), locations=()):
        if record_type.value[0] == '+':
            self.do_add_snap()

        record = {
            'timestamp': time.time(),
            'type': record_type,
            'message': message,
            'values': values,
            'locations': locations,
            'image_id': self.tracker.snaps,
            'page_id': self.tracker.page_id,
        }

        self.new_record(record)

    def do_on_new_page(self):
        pass

    def do_add_snap(self):
        pass

    def serialize(self, record):
        return {
            'timestamp': record['timestamp'],
            'type': record['type'].value,
            'message': record['message'],
            'values': record['values'],
            'locations': record['locations'],
            'image_id': record['image_id'],
            'page_id': record['page_id']
        }

    def print_record(self, record):
        output = "{0}: {1}".format(record['type'], record['message'])

        if record['values']:
            output += " Values={0!r}".format(record['values'])
        print output


class WriteAsYouGo(WriterBase):

    def new_record(self, record):
        """
        Prints the tracked record to standard out.
        Overridable method for performing an action on tracking.
        """
#TODO        output = "{0}: {1}".format(self.Record(record['type']), record['message'])
        self.print_record(record)

    def do_output_all_records(self):
        pass


class RecordAsYouGo(WriterBase): #TODO

    def new_record(self, record):
        """
        """
        record_type = record['type'].value
        if record['type'] in self.tracker.FILTER_EVENT_TYPES:
            return
        if record_type[0] in self.tracker.FILTER_INIT_CHARS:
            record_type = record_type[1:]
        record['type'] = record_type
        self.tracker.recorder_svc.new_record(record)

    def do_output_all_records(self):
        pass


class WriteAtTheEnd(WriterBase):
    def __init__(self, tracker):
        WriterBase.__init__(self, tracker)
        self.records = []

    def new_record(self, record):
        self.records.append(record)

    def do_output_all_records(self):
        """
        Outputs all records
        Overridable method for performing an action on tracking.
        """
#TODO        print "All events for %s:" % self.tst_name
        for record in self.records:
            self.print_record(record)


class JsonWriter(WriterBase):
    """Tracks and displays to Standard out and drops a JSON file of the records."""

    MAX_TST_NAME_LENGTH = 230  # This is due to OS filename length limitations.

    def __init__(self, tracker):
        WriterBase.__init__(self, tracker)
        self.tracker = tracker
        self.records = []
        self.snaps = []
        self.tst_name = self.tracker.auto.find_automation_complete_name()
        if len(self.tst_name) > self.MAX_TST_NAME_LENGTH:
            self.tst_name = self.tst_name[:self.MAX_TST_NAME_LENGTH] + '...'

    @staticmethod
    def get_snapshot_dir():
        snapshot_dir = config.my_cfg.config.get('SNAPSHOT_DIR', '')
        if snapshot_dir:
            if config.my_cfg.config.get('SNAPSHOT_DIR_AUTOCREATE', False) and not os.path.exists(snapshot_dir):
                print "Autocreating snapshot dir: %r" % snapshot_dir
                os.makedirs(snapshot_dir)
        else:
            snapshot_dir = tempfile.gettempdir()

        return snapshot_dir

    def new_record(self, record):
        self.records.append(record)

    def do_output_all_records(self):
        snapshot_dir = self.get_snapshot_dir()

        record_data = {
            'metadata': {
                        'tst_name': self.tst_name,
            },
            'directory': snapshot_dir,
            'records': [self.serialize(r) for r in self.records],
            'snaps': self.snaps,
        }

        json_path = os.path.join(snapshot_dir, '%s_records.json' % self.tst_name)
        json_file = open(json_path, mode='w')
        json.dump(record_data, json_file, indent=2)
        print "Writing all records to:", json_path


class ReplayWriter(JsonWriter):
    """Tracks and drops a JSON file of the records and supplies replay files."""

# TODO move to Replay.  not needed in json dump.
    def do_add_snap(self):
        if not config.my_cfg.config.get('SAVE_SCREENSHOT', 'False'):
            return

        snapshot_dir = self.get_snapshot_dir()
        snap_name = "%s_%03d.png" % (self.tst_name, self.tracker.snap_count)
        snap_path = os.path.join(snapshot_dir, snap_name)

        self.tracker.auto.start.save_snap_file(snap_path)
        self.snaps.append(snap_name)
        self.do_track(self.tracker.Record.SNAP, snap_name)

    def do_output_all_records(self):
        JsonWriter.do_output_all_records(self)
        snapshot_dir = self.get_snapshot_dir()

        # Copy over the replay files
        replay_path = os.path.join(snapshot_dir, '%s.html' % self.tst_name)
        shutil.copy("replay/main.js", snapshot_dir)
        shutil.copy("replay/styles.css", snapshot_dir)

        # Edit the HTML to have the test name
        self._write_out_template("replay/replay.html", replay_path)
        print "Writing all info to:", replay_path


    def _write_out_template(self, orig_filename, out_filename):
        with open(out_filename, "w") as fout:
            with open(orig_filename, "r") as fin:
                for line in fin:
                    fout.write(line.replace('##TEST_RUN_ID##', self.tst_name))

