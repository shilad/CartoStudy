import re

from collections import defaultdict, Counter

from log_utils import read_log


VERIFICATION = {
    'verification/The Lord of the Rings: The Fellowship of the Ring.jpg' : 'The Lord of the Rings: The Fellowship of the Ring',
    'verification/Rocky II.jpg' : 'Rocky II'
}



def main(log_dir):
    records = list(read_log(log_dir))
    cleaned = basic_log_stats(records)
    guesses = parse_guesses(cleaned)
    basic_guess_stats(guesses)



def basic_log_stats(records):
    print('basic statistics:')
    print('\t%d raw log records' % len(records))

    # Remove invalid workers (Shilad, Bret, 'None')
    cleaned = []
    for r in records:
        if len(r.workerId) > 6:
            cleaned.append(r)
    print('\t%d log records after removing fake worker ids' % len(cleaned))

    # Remove workers who don't complete the survey
    valid = set([r.workerId for r in cleaned if r.event == 'code'])
    cleaned = [r for r in cleaned if r.workerId in valid]
    print('')
    print('\t%d log records after removing worker ids who didnt finish' % len(cleaned))
    print('\t%d real workers finished' % len(valid))

    # Remove workers who didn't validate
    for r in cleaned:
        if r.event == 'map':
            m = r.info['map']
            if m in VERIFICATION and VERIFICATION[m] != r.info['first'] != 'Rocky II':
                if r.workerId in valid:
                    valid.remove(r.workerId)
    cleaned = [r for r in cleaned if r.workerId in valid]
    print('')
    print('\t%d log records after removing worker ids who didnt validate' % len(cleaned))
    print('\t%d real workers validated' % len(valid))

    # Demographics for validated workers:
    demographics = {
        'gender' : defaultdict(int),
        'educationlevel' : defaultdict(int),
        'Movie Frequency' : defaultdict(int),
        'seenMovies' : defaultdict(int),
        'age' : defaultdict(int),
    }

    for r in cleaned:
        if r.event == 'page' and r.info == 'bio/save':
            for k in r.params:
                v = r.params[k][0].lower().strip()
                if k in demographics:
                    demographics[k][v] += 1
            demographics['seenMovies'][len(r.params['seenMovies'])] += 1

    for field in demographics:
        print('values for ' + field)
        for k in sorted(demographics[field].keys()):
            v = demographics[field][k]
            print('\t%s: %d' % (k, v))

    maxes = {}
    mins = {}
    for r in cleaned:
        if r.workerId not in mins:
            mins[r.workerId] = r.tstamp
            maxes[r.workerId] = r.tstamp
        else:
            mins[r.workerId] = min(r.tstamp, mins[r.workerId])
            maxes[r.workerId] = max(r.tstamp, maxes[r.workerId])

    diffs = sorted([maxes[w] - mins[w] for w in maxes])
    print('mean completion time is %.0f seconds' % (sum(diffs) / len(diffs)))
    print('median completion time is %.0f seconds' % (diffs[len(diffs) / 2]))

    print('Top words:')
    words = Counter()
    for r in cleaned:
        if r.event == 'page' and r.info == 'thanks/save':
            comment = r.params['comments'][0].strip()
            if comment:
                for c in comment.split():
                    words[c.lower()] += 1
                print(comment)
    for (k, n) in words.most_common(20):
        print('\t%s=%d' % (k, n))

    return cleaned


MAT_MAP = re.compile('([a-z]+)/cartoScreenshots-(.*).jpg').match

def parse_guesses(records):
    guesses = []    # workerid, mapname, movie, guess
    for r in records:
        if r.event == 'map':
            m = r.info['map']
            if not m.startswith('verification'):
                match = MAT_MAP(r.info['map'])
                assert(match)
                guess = r.info['first']
                guesses.append((r.workerId, match.group(1), match.group(2), guess))

    guess_info = defaultdict(dict)
    for (workerId, mapname, movie, guess) in guesses:
        guess_info[(workerId, movie)][mapname] = guess
        guess_info[(workerId, movie)]['actual'] = movie

    return [g for g in guess_info.values() if len(g) == 3]

def basic_guess_stats(guesses):
    print('')
    print('basic guess information:')
    print('\t%d total guesses' % (len(guesses)))

    by_movie = defaultdict(list)
    for g in guesses:
        by_movie[g['actual']].append(g)

    contentHitsByMovie = defaultdict(int)
    navHitsByMovie = defaultdict(int)
    contentHits = 0
    navHits = 0
    for g in guesses:
        act = g['actual']
        if g['content'] == g['actual']:
            contentHits += 1
            contentHitsByMovie[act] += 1
        if g['nav'] == g['actual']:
            navHits += 1
            navHitsByMovie[act] += 1

    print('')
    print('content accuracy: %d of %d (%.1f%%)' % (contentHits, len(guesses), 100.0 * contentHits / len(guesses)))
    print('nav accuracy: %d of %d (%.1f%%)' % (navHits, len(guesses), 100.0 * navHits / len(guesses)))

    print('')
    navBetter = 0
    for m in sorted(by_movie.keys()):
        if contentHitsByMovie[m] < navHitsByMovie[m]:
            navBetter += 1
        print('\t%s: %d users content=%d/%d, nav=%d/%d' %
              (m, len(by_movie[m]),
               contentHitsByMovie[m], len(by_movie[m]),
               navHitsByMovie[m], len(by_movie[m])))
    print('navigation vectors better for %d of %d movies' % (navBetter, len(by_movie)))

if __name__ == '__main__':
    main('logs/prod')



