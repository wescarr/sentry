import GroupStore from 'sentry/stores/groupStore';
import {Group, GroupStats, TimeseriesValue} from 'sentry/types';

const g = (id: string, params?: Partial<Group>) => TestStubs.Group({id, ...params});

describe('GroupStore', function () {
  beforeEach(function () {
    GroupStore.reset();
  });

  describe('add()', function () {
    it('should add new entries', function () {
      GroupStore.items = [];
      GroupStore.add([g('1'), g('2')]);

      expect(GroupStore.items).toEqual([g('1'), g('2')]);
    });

    it('should update matching existing entries', function () {
      GroupStore.items = [g('1'), g('2')];

      GroupStore.add([{id: '1', foo: 'bar'}, g('3')]);

      expect(GroupStore.getAllItemIds()).toEqual(['1', '2', '3']);
      expect(GroupStore.items[0]).toEqual(expect.objectContaining({id: '1', foo: 'bar'}));
    });

    it('should attempt to preserve order of ids', function () {
      GroupStore.add([g('2'), g('1'), g('3')]);
      expect(GroupStore.getAllItemIds()).toEqual(['2', '1', '3']);
    });
  });

  describe('remove()', function () {
    it('should remove entry', function () {
      GroupStore.items = [g('1'), g('2')];
      GroupStore.remove(['1']);

      expect(GroupStore.items).toEqual([g('2')]);
    });

    it('should remove multiple entries', function () {
      GroupStore.items = [g('1'), g('2'), g('3')];
      GroupStore.remove(['1', '2']);

      expect(GroupStore.items).toEqual([g('3')]);
    });

    it('should not remove already removed item', function () {
      GroupStore.items = [g('1'), g('2')];
      GroupStore.remove(['0']);

      expect(GroupStore.items).toEqual([g('1'), g('2')]);
    });
  });

  describe('onMergeSuccess()', function () {
    it('should remove the non-parent merged ids', function () {
      GroupStore.items = [g('1'), g('2'), g('3'), g('4')];

      GroupStore.onMergeSuccess(
        '',
        ['2', '3', '4'], // items merged
        {merge: {parent: '3'}} // merge API response
      );

      expect(GroupStore.items).toEqual([
        g('1'),
        g('3'), // parent
      ]);
    });
  });

  describe('onPopulateStats()', function () {
    let triggerSpy: jest.SpyInstance;

    const stats: Record<string, TimeseriesValue[]> = {auto: [[1611576000, 10]]};

    beforeAll(function () {
      triggerSpy = jest.spyOn(GroupStore, 'trigger');
    });
    beforeEach(function () {
      triggerSpy.mockReset();
      GroupStore.items = [g('1'), g('2'), g('3')];
    });

    it('should merge stats into existing groups', function () {
      GroupStore.onPopulateStats(
        ['1', '2', '3'],
        [
          {id: '1', stats} as GroupStats,
          {id: '2', stats} as GroupStats,
          {id: '3', stats} as GroupStats,
        ]
      );

      const group = GroupStore.getAllItems()[0] as Group;

      expect(group.stats).toEqual(stats);
      expect(GroupStore.trigger).toHaveBeenCalledWith(new Set(['1', '2', '3']));
    });

    it('should not change current item ids', function () {
      GroupStore.onPopulateStats(
        ['2', '3'],
        [{id: '2', stats} as GroupStats, {id: '3', stats} as GroupStats]
      );

      const group1 = GroupStore.getAllItems()[0] as Group;
      const group2 = GroupStore.getAllItems()[1] as Group;

      expect(GroupStore.trigger).toHaveBeenCalledWith(new Set(['2', '3']));
      expect(group1.stats).not.toEqual(stats);
      expect(group2.stats).toEqual(stats);
    });
  });

  describe('getAllItems()', function () {
    it('Merges pending changes into items', function () {
      GroupStore.items = [];
      GroupStore.add([g('1'), g('2')]);

      GroupStore.onUpdate('1337', ['1'], {someChange: true});

      expect(GroupStore.get('1')).toEqual(
        expect.objectContaining({id: '1', someChange: true})
      );
    });
  });

  describe('update methods', function () {
    let triggerSpy: jest.SpyInstance;

    beforeAll(function () {
      triggerSpy = jest.spyOn(GroupStore, 'trigger');
    });
    beforeEach(function () {
      triggerSpy.mockReset();
    });

    beforeEach(function () {
      GroupStore.items = [g('1'), g('2'), g('3')];
    });

    describe('onUpdate()', function () {
      it("should treat undefined itemIds argument as 'all'", function () {
        GroupStore.onUpdate('1337', undefined, {});

        expect(GroupStore.trigger).toHaveBeenCalledTimes(0);
      });
    });

    describe('onUpdateSuccess()', function () {
      it("should treat undefined itemIds argument as 'all'", function () {
        GroupStore.onUpdateSuccess('1337', undefined, {});

        expect(GroupStore.trigger).toHaveBeenCalledTimes(1);
        expect(GroupStore.trigger).toHaveBeenCalledWith(new Set(['1', '2', '3']));
      });
    });

    describe('onUpdateError()', function () {
      it("should treat undefined itemIds argument as 'all'", function () {
        GroupStore.onUpdateError('1337', undefined, false);

        expect(GroupStore.trigger).toHaveBeenCalledTimes(1);
        expect(GroupStore.trigger).toHaveBeenCalledWith(new Set(['1', '2', '3']));
      });
    });

    describe('onDeleteSuccess()', function () {
      it("should treat undefined itemIds argument as 'all'", function () {
        GroupStore.onDeleteSuccess('1337', undefined, {});

        expect(GroupStore.trigger).toHaveBeenCalledTimes(1);
        expect(GroupStore.trigger).toHaveBeenCalledWith(new Set(['1', '2', '3']));
      });
    });
  });
});
