import reducer, {
    removeResultSort,
    SORT_ORDER,
    updateResultSort
} from './searchSlice';
import { createNextState } from "@reduxjs/toolkit";
import { searchInfoData } from "./SearchPage.stories";

describe("Sort reducers", () => {

    it("can add sort in the order they are added", () => {
        const expectedSearchState = createNextState(searchInfoData, draft => {
            draft.sort.project.push({
                id: "createdDate",
                order: SORT_ORDER.ascending
            });
        });
        expect(reducer(searchInfoData, updateResultSort({
            typeId: "project",
            attributeId: "createdDate",
            order: SORT_ORDER.ascending
        }))).toEqual(expectedSearchState);
    });

    it("can remove the correct sort option", () => {
        const expectedSearchState = createNextState(searchInfoData, draft => {
            draft.sort.project = [
                { id: "description", order: SORT_ORDER.ascending}
            ];
        });
        expect(reducer(searchInfoData, removeResultSort({
            typeId: "project",
            attributeId: "institution",
        }))).toEqual(expectedSearchState);
    });
});