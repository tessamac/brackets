#!/usr/local/bin/python3.5
import brackets
import unittest
import unittest.mock


class BracketsTest(unittest.TestCase):

  def setUp(self):
    # For testing, don't shuffle.
    self.mock_shuffle = unittest.mock.patch.object(brackets, 'Shuffle').start()

  def tearDown(self):
    self.mock_shuffle.stop()

  def testGetValues(self):
    values = brackets.GetValues('values.txt')
    self.assertEqual(145, len(values))
    self.assertEqual('Accountability', values[0])
    self.assertEqual('Vitality', values[-1])

  def testShuffle(self):
    # Doesn't actually shuffle because it was mocked.
    items = [0, 1, 2, 3]
    brackets.Shuffle(items)
    self.assertEqual([0, 1, 2, 3], items)

  def testKeep(self):
    with unittest.mock.patch.object(
        brackets, 'GetInput', return_value='y') as mock_getinput:
      self.assertTrue(brackets.Keep('foo'))
      mock_getinput.assert_called_once_with('foo? [y/N] ')

    with unittest.mock.patch.object(
        brackets, 'GetInput', return_value='Y') as mock_getinput:
      self.assertFalse(brackets.Keep('foo'))
      mock_getinput.assert_called_once_with('foo? [y/N] ')

    with unittest.mock.patch.object(
        brackets, 'GetInput', return_value='n') as mock_getinput:
      self.assertFalse(brackets.Keep('foo'))
      mock_getinput.assert_called_once_with('foo? [y/N] ')

    with unittest.mock.patch.object(
        brackets, 'GetInput', return_value='N') as mock_getinput:
      self.assertFalse(brackets.Keep('foo'))
      mock_getinput.assert_called_once_with('foo? [y/N] ')

    with unittest.mock.patch.object(
        brackets, 'GetInput', return_value=None) as mock_getinput:
      self.assertFalse(brackets.Keep('foo'))
      mock_getinput.assert_called_once_with('foo? [y/N] ')

  def testCompare(self):
    with unittest.mock.patch.object(
        brackets, 'GetInput', return_value='y') as mock_getinput:
      self.assertEqual(1, brackets.Compare('foo', 'bar'))
      mock_getinput.assert_called_once_with('foo even over bar? [y/N] ')

    with unittest.mock.patch.object(
        brackets, 'GetInput', return_value='Y') as mock_getinput:
      self.assertEqual(-1, brackets.Compare('foo', 'bar'))
      mock_getinput.assert_called_once_with('foo even over bar? [y/N] ')

    with unittest.mock.patch.object(
        brackets, 'GetInput', return_value='n') as mock_getinput:
      self.assertEqual(-1, brackets.Compare('foo', 'bar'))
      mock_getinput.assert_called_once_with('foo even over bar? [y/N] ')

    with unittest.mock.patch.object(
        brackets, 'GetInput', return_value='N') as mock_getinput:
      self.assertEqual(-1, brackets.Compare('foo', 'bar'))
      mock_getinput.assert_called_once_with('foo even over bar? [y/N] ')

    with unittest.mock.patch.object(
        brackets, 'GetInput', return_value=None) as mock_getinput:
      self.assertEqual(-1, brackets.Compare('foo', 'bar'))
      mock_getinput.assert_called_once_with('foo even over bar? [y/N] ')

  def testFilter(self):
    with unittest.mock.patch.object(
        brackets, 'GetInput', return_value=None) as mock_getinput:
      self.assertEqual([], brackets.Filter(['foo']))
      mock_getinput.assert_called_once_with('foo? [y/N] ')

    with unittest.mock.patch.object(
        brackets, 'GetInput', return_value='y') as mock_getinput:
      self.assertEqual(['foo'], brackets.Filter(['foo']))
      mock_getinput.assert_called_once_with('foo? [y/N] ')

    # Discard the first, keep the second.
    return_values = [None, 'y']
    with unittest.mock.patch.object(
        brackets, 'GetInput', side_effect=return_values) as mock_getinput:
      self.assertEqual([1], brackets.Filter([0, 1]))
      self.assertEqual(2, mock_getinput.call_count)

  def testHeadToHead_One(self):
    candidates = [brackets.Candidate('foo')]

    with unittest.mock.patch.object(
        brackets, 'GetInput', return_value='y') as mock_getinput:
      winners = brackets.HeadToHead(candidates)
      self.assertEqual(0, mock_getinput.call_count)

      self.assertEqual(1, len(winners))
      self.assertEqual('foo', winners[0].name)
      self.assertEqual([], winners[0].losers)

  def testHeadToHead_Two(self):
    candidates = [brackets.Candidate('foo'), brackets.Candidate('bar')]

    # Keep 'bar'.
    with unittest.mock.patch.object(
        brackets, 'GetInput', return_value='y') as mock_getinput:
      winners = brackets.HeadToHead(candidates)
      mock_getinput.assert_called_once_with('bar even over foo? [y/N] ')

      self.assertEqual(1, len(winners))
      self.assertEqual('bar', winners[0].name)
      self.assertEqual(1, len(winners[0].losers))
      self.assertEqual('foo', winners[0].losers[0].name)

  def testHeadToHead_Many(self):
    names = ['foo', 'bar', 'baz', 'bam', 'boom']
    candidates = []
    for n in names:
      candidates.append(brackets.Candidate(n))

    return_values = ['y', None]
    with unittest.mock.patch.object(
        brackets, 'GetInput', side_effect=return_values) as mock_getinput:
      winners = brackets.HeadToHead(candidates)
      self.assertEqual(2, mock_getinput.call_count)
      mock_getinput.assert_has_calls(
          [unittest.mock.call('boom even over bam? [y/N] '),
           unittest.mock.call('baz even over bar? [y/N] ')])

      self.assertEqual(3, len(winners))
      # boom beat bam
      self.assertEqual('boom', winners[0].name)
      self.assertEqual('bam', winners[0].losers[0].name)
      # bar beat baz
      self.assertEqual('bar', winners[1].name)
      self.assertEqual('baz', winners[1].losers[0].name)
      # foo is a winner because there were no more candidates for comparison
      self.assertEqual('foo', winners[2].name)
      self.assertEqual([], winners[2].losers)

  def testFindTopN_One(self):
    return_values = ['y', 'y', None, 'y']
    with unittest.mock.patch.object(
        brackets, 'GetInput', side_effect=return_values) as mock_getinput:
      names = [1, 2, 3, 4, 5]
      winners = brackets.FindTopN(names, n=1)
      self.assertEqual(4, mock_getinput.call_count)
      mock_getinput.assert_has_calls(
          [unittest.mock.call('5 even over 4? [y/N] '),
           unittest.mock.call('3 even over 2? [y/N] '),
           unittest.mock.call('1 even over 3? [y/N] '),
           unittest.mock.call('5 even over 3? [y/N] ')])
      self.assertEqual([5], winners)

  def testFindTopN_Two(self):
    return_values = [None, 'y', None, None, None, None]
    with unittest.mock.patch.object(
        brackets, 'GetInput', side_effect=return_values) as mock_getinput:
      names = [4, 3, 5, 2, 1]
      winners = brackets.FindTopN(names, n=2)
      self.assertEqual(6, mock_getinput.call_count)
      mock_getinput.assert_has_calls(
          [unittest.mock.call('1 even over 2? [y/N] '),
           unittest.mock.call('5 even over 3? [y/N] '),
           unittest.mock.call('4 even over 5? [y/N] '),
           unittest.mock.call('2 even over 5? [y/N] '),
           unittest.mock.call('2 even over 4? [y/N] '),
           unittest.mock.call('3 even over 4? [y/N] ')])
      self.assertEqual([5, 4], winners)

  def testFindTopN_Three(self):
    return_values = [None, None, 'y', None, 'y', 'y']
    with unittest.mock.patch.object(
        brackets, 'GetInput', side_effect=return_values) as mock_getinput:
      names = [5, 3, 1, 4, 2]
      winners = brackets.FindTopN(names, n=3)
      self.assertEqual(6, mock_getinput.call_count)
      mock_getinput.assert_has_calls(
          [unittest.mock.call('2 even over 4? [y/N] '),
           unittest.mock.call('1 even over 3? [y/N] '),
           unittest.mock.call('5 even over 3? [y/N] '),
           unittest.mock.call('4 even over 5? [y/N] '),
           unittest.mock.call('4 even over 3? [y/N] '),
           unittest.mock.call('3 even over 2? [y/N] ')])
      self.assertEqual([5, 4, 3], winners)

  def testFindTopN_Four(self):
    return_values = [None, 'y', 'y', 'y', None]
    with unittest.mock.patch.object(
        brackets, 'GetInput', side_effect=return_values) as mock_getinput:
      names = [3, 1, 2, 5, 4]
      winners = brackets.FindTopN(names, n=4)
      self.assertEqual(5, mock_getinput.call_count)
      mock_getinput.assert_has_calls(
          [unittest.mock.call('4 even over 5? [y/N] '),
           unittest.mock.call('2 even over 1? [y/N] '),
           unittest.mock.call('3 even over 2? [y/N] '),
           unittest.mock.call('5 even over 3? [y/N] '),
           unittest.mock.call('3 even over 4? [y/N] ')])
      self.assertEqual([5, 4, 3, 2], winners)

  def testFindTopN_Five(self):
    return_values = [None, 'y', None, None,'y', None, 'y', None, None]
    with unittest.mock.patch.object(
        brackets, 'GetInput', side_effect=return_values) as mock_getinput:
      names = [2, 3, 5, 4, 1]
      winners = brackets.FindTopN(names, n=5)
      self.assertEqual(9, mock_getinput.call_count)
      mock_getinput.assert_has_calls(
          [unittest.mock.call('1 even over 4? [y/N] '),
           unittest.mock.call('5 even over 3? [y/N] '),
           unittest.mock.call('2 even over 5? [y/N] '),
           unittest.mock.call('4 even over 5? [y/N] '),
           unittest.mock.call('4 even over 2? [y/N] '),
           unittest.mock.call('3 even over 4? [y/N] '),
           unittest.mock.call('3 even over 2? [y/N] '),
           unittest.mock.call('1 even over 3? [y/N] '),
           unittest.mock.call('1 even over 2? [y/N] ')])
      self.assertEqual([5, 4, 3, 2, 1], winners)


if __name__ == '__main__':
  unittest.main()
