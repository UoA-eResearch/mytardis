/* eslint-disable no-undef */
import reducer, {
    removeResultSort,
    SORT_ORDER,
    updateResultSort,
    parseQuery
} from './searchSlice';
import { createNextState } from "@reduxjs/toolkit";
import { searchInfoData } from "./SearchPage.stories";

describe("Query parser", () => {
    it("can parse text search terms", () => {
        expect(parseQuery("?q=abc")).toEqual({query: "abc"});
    });

    it("can parse numerical search terms", () => {
        expect(parseQuery("?q=2")).toEqual({query: "2"});
    });

    it("can parse complex search query", () => {
        expect(parseQuery("?q={\"filters\":\"1\"}")).toEqual({filters: "1"});
    });

    it("can parse special characters", () => {
        expect(parseQuery("?q=%3A")).toEqual({query: ":"});
    });

    it("can parse square brackets as a search term", () => {
        expect(parseQuery("?q=%5B2%5D")).toEqual({query: "[2]"});
    });
});

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
