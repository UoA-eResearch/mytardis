import { parseQuery } from "./searchSlice";

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
    })
});