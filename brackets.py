#!/usr/bin/python
import random


def GetValues(file_name):
  """Read lines from a text file."""
  values = []
  with open(file_name) as f:
    values = f.read().splitlines()
  return values


def GetInput():
  """For easy mocking."""
  return raw_input


def Shuffle(items):
  """For easy mocking."""
  random.shuffle(items)


def Keep(item):
  """Return True if item should be kept, False if it should be discarded."""
  c = GetInput('%s? [y/N] ' % item)
  return c == 'y'


def Compare(first, second):
  """Return positive if the first is preferred, negative if the second is."""
  c = GetInput('%s even over %s? [y/N] ' % (first, second))
  if c == 'y':
    return 1
  else:
    return -1


def Filter(items):
  """Check if we should keep each item."""
  keepers = []
  for item in items:
    if Keep(item):
      keepers.append(item)
  return keepers


class Candidate:
  """A single head-to-head candidate with a list of those it has beat."""
  def __init__(self, name):
    self.name = name
    self.losers = []

  def __repr__(self):
    return '%s beat: %s' % (self.name, self.losers)


def HeadToHead(candidates):
  """Run one level of head-to-head comparisons for the candidates. """
  Shuffle(candidates)
  winners = []

  while len(candidates) >= 2:
    candidate1 = candidates.pop()
    candidate2 = candidates.pop()
    if Compare(candidate1.name, candidate2.name) > 0:
      winner = candidate1
      winner.losers.append(candidate2)
    else:
      winner = candidate2
      winner.losers.append(candidate1)
    winners.append(winner)

  # If there is a remaining candidate it autmatically wins.
  if len(candidates) > 0:
    winners.append(candidates[0])

  return winners


def FindTopN(items, n=3):
  """Get a list of the best n by running head-to-head comparisons."""
  candidates = []
  for item in items:
    candidates.append(Candidate(item))

  tops = []
  for i in range(n):
    winners = HeadToHead(candidates)
    while len(winners) > 1:
      winners = HeadToHead(winners)
    tops.append(winners[0].name)
    candidates = winners[0].losers

  return tops


def main():
  values = GetValues('values.txt')

  # Quickly throw out the bad ones.
  if len(values) > 50:
    keepers = Filter(values)

  top3 = FindTopN(values, n=3)
  print(top3)


if __name__ == "__main__":
    main()
