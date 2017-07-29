import os
import sqlite3 as sqlite

from os import path
from csv import reader,DictReader


from ReportWriter import ReportWriter
from model.IEvaluator import IEvaluator
from model.IResultAnalyzer import IResultAnalyzer


class ResultAnalyzer(IResultAnalyzer):

    REPORTS_DIR = 'reports'
    RESULTS_DIR = 'results'
    RESULTS_SUMMARY = 'summary.csv'

    CMD_SUMMARY = 'summary'
    CMD_SUCC = 'successes'
    CMD_FAILS = 'fails'
    CMD_OUTS = 'outs'
    CMD_CHECK = 'check'
    CMD_EXPORT_DB = 'exportsql'

    LOG_TAG = "ResultAnalyzer"

    def __init__(self, out_dir, evaluator, fixed_fields_front, fixed_fields_back):

        self.out_dir = out_dir

        self.summary_file = path.join(out_dir, ResultAnalyzer.RESULTS_DIR,
                                      evaluator.get_eval_id() + "_" + ResultAnalyzer.RESULTS_SUMMARY)

        self.evaluator = evaluator

        # caching
        self.subtasks = evaluator.get_subtask_ids_ordered()
        self.interpretations = evaluator.get_subtask_interpretation()
        self.required_subtasks = [subtask for subtask in self.subtasks
                                  if self.interpretations[subtask] == IEvaluator.REQUIRED]
        self.assumed_subtasks = [subtask for subtask in self.subtasks
                                  if self.interpretations[subtask] == IEvaluator.ASSUMPTION]
        self.dontcare_subtasks = [subtask for subtask in self.subtasks
                                 if self.interpretations[subtask] == IEvaluator.DONTCARE]

        self.fixed_fields_front = fixed_fields_front
        self.fixed_fields_back = fixed_fields_back
        self.ordered_fieldnames = self.fixed_fields_front + self.subtasks + self.fixed_fields_back

    ### interface

    # returns bool
    def is_success(self, summary_row):
        return self.interpret(summary_row) == IResultAnalyzer.SUCCESS

    # returns bool
    def is_out(self, summary_row):
        return self.interpret(summary_row) == IResultAnalyzer.OUT

    # returns bool
    def is_failure(self, summary_row):
        return self.interpret(summary_row) == IResultAnalyzer.FAIL

    # returns interpretation of row as either FAIL, OUT or SUCCESS for well-formed rows
    # and None for headlines, comments and the like
    def interpret(self, summary_row):
        for subtask in self.subtasks:

            # sanity check
            if subtask not in self.interpretations.keys():
                self.log('Error! No interpretation available for subtask ' + subtask)
                exit(-1)

            interpretation = self.interpretations[subtask]
            subtask_result = summary_row[subtask]
            if not self.is_app_row(summary_row):
                # invalid
                return None
            subtask_success = (subtask_result == 'True')
            # sanity check
            if not subtask_success and subtask_result != 'False':
                self.log('Unexpected value for subtask ' + subtask + ': ' + subtask_result)
                self.log(summary_row)
                exit(-1)

            if interpretation == IEvaluator.DONTCARE:
                continue
            if not subtask_success:
                if interpretation == IEvaluator.REQUIRED:
                    # count as fail
                    return IResultAnalyzer.FAIL
                elif interpretation == IEvaluator.ASSUMPTION:
                    # remove from counting
                    # self.log('Removing row because assumption ' + subtask + ' was not met:')
                    # self.log(row)
                    return IResultAnalyzer.OUT
                else:
                    self.log('Error! Unexpected interpretation for subtask ' + subtask + ': ' + interpretation)
                    exit(-1)
        # no fails (that we care about) occurred
        return IResultAnalyzer.SUCCESS

    # returns all summary rows in a tuple: (tested, outs, failures, successes)
    def get_all(self):
        # if this method ever gets too slow because the data is too big: implement in one interation
        tested = self.get_tested()
        outs = self.get_outs(csv_rows=tested)
        fails = self.get_fails(csv_rows=tested)
        successes = self.get_successes(csv_rows=tested)
        return tested, outs, fails, successes

    # returns all summary rows
    def get_tested(self):
        # filter out non-data rows (comments, headlines, ...)
        return self.find_matching_entries(lambda row: self.interpret(row) is not None)

    # returns summary rows from apps that did not meet the assumptions
    def get_outs(self, csv_rows=None):
        if not csv_rows:
            csv_rows = self.get_app_rows()
        return self.find_matching_entries(self.is_out, csv_rows=csv_rows)

    # returns summary rows from apps that failed
    def get_fails(self, csv_rows=None):
        if not csv_rows:
            csv_rows = self.get_app_rows()
        return self.find_matching_entries(self.is_failure, csv_rows=csv_rows)

    # returns summary rows from apps that succeeded
    def get_successes(self, csv_rows=None):
        if not csv_rows:
            csv_rows = self.get_app_rows()
        return self.find_matching_entries(self.is_success, csv_rows=csv_rows)

    # extend this in eval-specific subclasses
    # binds commands to methods. API methods are required to have zero parameters
    def get_command_api(self):
        return {
            ResultAnalyzer.CMD_SUMMARY: self.api_summary,
            ResultAnalyzer.CMD_CHECK: self.api_check,
            ResultAnalyzer.CMD_SUCC: self.get_successes,
            ResultAnalyzer.CMD_FAILS: self.api_failures,
            ResultAnalyzer.CMD_OUTS: self.get_outs,
            ResultAnalyzer.CMD_EXPORT_DB: self.api_export_sql
        }

    ### API implementation ###

    # API for command CMD_SUMMARY
    def api_summary(self):

        # category -> (tests, outs, fails, successes)
        results = dict()

        # use list since tuples do not support item assignment
        overall = [0, 0, 0, 0]

        for row in self.get_app_rows():
            app = row[ReportWriter.KEY_PKG]
            categories = row[ReportWriter.KEY_CATS].strip().split(ReportWriter.CSV_IN_CELL_SEPARATOR)
            for cat in categories:
                if cat not in results.keys():
                    # use list since tuples do not support item assignment
                    results[cat] = [0, 0, 0, 0]

                # increase number of tests
                results[cat][0] += 1
                overall[0] += 1

                # none not possible since we iterate over checked app rows
                interpretation = self.interpret(row)
                if interpretation == IResultAnalyzer.OUT:
                    results[cat][1] += 1
                    overall[1] += 1
                    continue
                if interpretation == IResultAnalyzer.FAIL:
                    results[cat][2] += 1
                    overall[2] += 1
                    continue
                if interpretation == IResultAnalyzer.SUCCESS:
                    results[cat][3] += 1
                    overall[3] += 1
                    continue
                raise AssertionError('Unknown interpretation: ' + interpretation)

        for cat in sorted(results.keys()):
            tests, outs, fails, successes = results[cat]
            included = tests - outs
            percentage = (successes / included) * 100 if included > 0 else 0
            self.log('Category ' + cat + ': Tested: ' + str(tests) + ', removed: ' + str(outs)
                     + ', success: ' + str(successes) + '/' + str(included) + ' = ' + str(percentage) + '%')

        overall_tests = overall[0]
        overall_outs = overall[1]
        overall_successes = overall[3]
        overall_included = overall_tests - overall_outs
        overall_percentage = (overall_successes / overall_included) * 100 if overall_included > 0 else 0
        self.log('Overall: Tested: ' + str(overall_tests) + ', removed: ' + str(overall_outs)
                 + ', success: ' + str(overall_successes) + '/' + str(overall_included) + ' = ' + str(overall_percentage) + '%')


    # API for command CMD_SUCC
    # find entries that succeeded
    def api_successes(self, dump=False):
        successes = self.get_successes()
        if dump:
            for row in successes:
                self.log(row[ReportWriter.KEY_PKG])

        self.log('Found ' + str(len(successes)) + ' successes.')

    # API for command CMD_FAILS
    # find entries that failed (excludes outs and successes)
    def api_failures(self, dump=False):
        failures = self.get_fails()
        if dump:
            for row in failures:
                self.log(row[ReportWriter.KEY_PKG])

        self.log('Found ' + str(len(failures)) + ' failures.')

    # API for command CMD_OUTS
    # find entries that are removed because assumptions are not met (excludes succeeded and failed ones)
    def api_outs(self, dump=False):
        outs = self.get_outs()
        if dump:
            for row in outs:
                self.log(row[ReportWriter.KEY_PKG])

        self.log('Found ' + str(len(outs)) + ' outs.')

    # API for command CMD_CHECK
    # check results for inconsistencies
    def api_check(self):

        row_dict = self.get_app_rows()

        # count occurences of package names
        packages_counter = dict() # mapping: package -> occurence
        for row in row_dict:

            for fieldname in row.keys():
                # check for unknown fieldname
                if not fieldname in self.fixed_fields_front + self.subtasks + self.fixed_fields_back:
                    self.log('Warning: Found unknown field: ' + fieldname)

            # remove header lines and comments
            if row[ReportWriter.KEY_TIMESTAMP] is None or row[ReportWriter.KEY_TIMESTAMP] == ReportWriter.KEY_TIMESTAMP:
                # self.log('Skipping entry: ' + str(row))
                continue
            package_name = row[ReportWriter.KEY_PKG]
            if package_name in packages_counter.keys():
                packages_counter[package_name] +=1
            else:
                packages_counter[package_name] = 1

        # find and print duplicates
        duplicates = [(package,count) for (package,count) in packages_counter.items() if count > 1]
        if len(duplicates) > 0:
            self.log(str(len(duplicates)) + ' duplicates:')
            for pkg, count in duplicates:
                self.log(pkg+ ': ' + str(count))
        else:
            self.log('No duplicates.')

    # API for command CMD_EXPORT_DB
    # exports the successful results into a sqlite database
    def api_export_sql(self):
        reportsPath = path.join(self.out_dir, ResultAnalyzer.REPORTS_DIR)
        dbPath = path.join(self.out_dir,'db.sqlite')
        dbConn = sqlite.connect(dbPath)
        db = dbConn.cursor()
        db.execute("CREATE TABLE results(packageId,vuln)")
        insertQuery = "INSERT INTO results values(?, ?)"
        rows = self.get_successes()
        for row in rows:
            changed = False
            packageId = row[ReportWriter.KEY_PKG]
            report = path.join(reportsPath, packageId)
            file = open(report, 'r')
            for line in file:
                internalChange = "";
                if "[DC]" in line:
                    line = line[line.index("[DC]"):]
                    internalChange = "[DC]";
                if "[TC]" in line:
                    line = line[line.index("[TC]"):]
                    internalChange = "[TC]";
                if len(internalChange) > 0:
                    changed = True
                    line = line[line.index(internalChange):]
                    if "[OBFUSCATED]" in line:
                        if not obfuscated:
                            obfuscated = True
                            db.execute(insertQuery, (packageId, line))
                            # print(packageId+':'+line)
                    else:
                        # print(packageId + ':' + line)
                        db.execute(insertQuery, (packageId, line))
            if not changed:
                # print(packageId + ': NOTHING FOUND')
                db.execute(insertQuery, (packageId, "Nothing found"))
        dbConn.commit()
        dbConn.close()

    ### helper methods ###

    def log(self, s):
        print(ResultAnalyzer.LOG_TAG + ": " + str(s))

    def read_csv_dict(self):
        result = []

        if path.isfile(self.summary_file):
            subtasks = self.evaluator.get_subtask_ids_ordered()

            with open(self.summary_file, 'r') as result_csv:
                csv_reader = DictReader(result_csv, delimiter=';', fieldnames=self.ordered_fieldnames)
                for row in csv_reader:
                    result.append(row)
        return result

    # returns list of row dicts
    def find_matching_entries(self, condition, csv_rows = None):
        results = []
        if not csv_rows:
            csv_rows = self.read_csv_dict()

        for row in csv_rows:
            if condition(row):
                results.append(row)
        return results

    # get all app entries from the summary csv, omitting categories and empty lines
    def get_app_rows(self):
        return self.find_matching_entries(self.is_app_row)

    # True if a given row is an app testing result, False otherwise (categories, header lines)
    def is_app_row(self, row):
        return row[ReportWriter.KEY_TIMESTAMP] is not None \
               and row[ReportWriter.KEY_TIMESTAMP] != ReportWriter.KEY_TIMESTAMP


