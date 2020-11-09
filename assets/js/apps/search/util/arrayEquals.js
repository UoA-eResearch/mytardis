/**
 * Given two Arrays of elements, returns a shallow equality comparison between the two.
 * @param {Array} arrayA Array of elements.
 * @param {Array} arrayB Array of elements to compare with.
 */
const arrayEquals = (arrayA, arrayB) => {
    if (arrayA === arrayB) {
        return true;
    }
    if (!Array.isArray(arrayA) || !Array.isArray(arrayB)) {
        return false;
    }
    if (arrayA.length !== arrayB.length) {
        return false;
    }
    const unequalElements = arrayA.filter ((value, index) => (value !== arrayB[index]));
    return unequalElements.length > 0; 
};

export default arrayEquals;