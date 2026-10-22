import importlib.util
from datetime import date, timedelta
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
import xml.etree.ElementTree as ET

spec=importlib.util.spec_from_file_location('activity',Path(__file__).resolve().parents[1]/'engineering_activity.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ActivityTests(unittest.TestCase):
    def test_calendar_counts_not_color_levels(self):
        p=m.CalendarParser()
        p.feed('<td id="a" data-date="2026-10-21" data-level="4"></td><tool-tip for="a">1,234 contributions on October 21st.</tool-tip><td id="b" data-date="2026-10-22"></td><tool-tip for="b">No contributions on October 22nd.</tool-tip>')
        self.assertEqual(p.days(),{'2026-10-21':1234,'2026-10-22':0})

    def test_missing_calendar_day_is_failure_not_zero(self):
        with self.assertRaises(ValueError):
            m.validate_days({'2026-10-21':1},date(2026,10,21),date(2026,10,22))

    def test_negative_count_rejected(self):
        with self.assertRaises(ValueError):
            m.validate_days({'2026-10-21':-1},date(2026,10,21),date(2026,10,21))

    def test_streak_current_today_yesterday_and_gap(self):
        for counts,expected in [([0,1,1],(2,2)),([0,1,1,0],(2,2)),([1,1,0,0],(0,2)),([0,0],(0,0))]:
            with self.subTest(counts=counts):
                self.assertEqual(m.streaks([{'count':c} for c in counts]),expected)

    def test_incomplete_search_cannot_be_metric(self):
        with patch.object(m,'api',return_value={'incomplete_results':True,'total_count':0}):
            with self.assertRaises(ValueError):m.search_count('x')

    def fixture(self):
        return json.loads((Path(__file__).resolve().parents[2]/'assets/engineering/snapshot.json').read_text(encoding='utf8'))

    def test_svg_all_variants_and_optional_metrics(self):
        data=self.fixture()
        for optional in (False,True):
            if optional:data.update(commit_contributions=123,commit_repositories=4)
            for theme in ('dark','light'):
                for mobile in (False,True):
                    svg=m.render(data,theme,mobile);ET.fromstring(svg)
                    self.assertEqual('Commit contributions' in svg,optional)
                    self.assertNotIn('<script',svg)
                    self.assertNotRegex(svg,r'(?:href|src)="https?://')

    def test_bad_snapshot_cannot_overwrite_last_good(self):
        data=self.fixture();data['contributions']+=1
        with tempfile.TemporaryDirectory(dir=m.ROOT) as directory:
            root=Path(directory);out=root/'assets/engineering';out.mkdir(parents=True)
            prior=out/'snapshot.json';prior.write_text('last good')
            with patch.object(m,'ROOT',root),patch.object(m,'OUTPUT',out):
                with self.assertRaises(ValueError):m.write_snapshot(data)
            self.assertEqual(prior.read_text(),'last good')

    def test_source_subject_escaping(self):
        data=self.fixture();data['projects'][0]['subject']='<script>[a]`x`'
        rendered=m.activity_markdown(data)
        self.assertNotIn('<script>',rendered)
        self.assertIn('&lt;script&gt;',rendered)


if __name__=='__main__':unittest.main()
