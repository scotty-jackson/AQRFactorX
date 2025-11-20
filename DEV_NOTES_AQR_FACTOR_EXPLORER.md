# AQR Factor Explorer - Developer Notes

## Overview
This document summarizes the improvements made to the AQR Factor Explorer web application, including functional fixes, UI/UX enhancements, code quality improvements, and testing setup.

## Application Architecture

### Tech Stack
- **Framework**: Next.js 14.1.0 (Pages Router)
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS 3.4.1
- **Charts**: Recharts 2.10.4
- **HTTP Client**: Axios 1.6.5
- **Testing**: Jest + React Testing Library

### Key Components
- `pages/factors/index.tsx` - Factor directory page with filters
- `components/FactorCard.tsx` - Factor card component
- `components/FactorCardSkeleton.tsx` - Loading skeleton
- `hooks/useFactorFilters.ts` - Reusable filter state management
- `lib/api.ts` - API client
- `lib/utils.ts` - Utility functions

## Changes Made

### 1. Error Handling & Robustness ✅

**Files Modified**: `pages/factors/index.tsx`

**Changes**:
- Added error state management with `useState<string | null>(null)`
- Wrapped API calls in try-catch blocks
- Added data validation to ensure API responses are arrays
- Implemented error UI with retry button
- Clear error state when filters change

**Why**: Prevents crashes when backend is unavailable and provides clear user feedback.

### 2. Improved Loading UX ✅

**Files Created**: `components/FactorCardSkeleton.tsx`  
**Files Modified**: `pages/factors/index.tsx`

**Changes**:
- Created skeleton loading component matching FactorCard layout
- Display 6 skeleton cards during loading instead of spinner
- Uses Tailwind `animate-pulse` for smooth loading animation

**Why**: Modern UX pattern that shows layout structure while loading, reducing perceived wait time.

### 3. Enhanced Empty States ✅

**Files Modified**: `pages/factors/index.tsx`

**Changes**:
- Added icon to empty state
- Different messages for filtered vs unfiltered empty states
- Only show "Clear Filters" button when filters are active

**Why**: Provides helpful context and guidance to users.

### 4. Tooltips on Metrics ✅

**Files Modified**: `components/FactorCard.tsx`

**Changes**:
- Added `title` attributes to each metric div
- Tooltips explain:
  - **Annualized Return**: Average yearly return of the factor
  - **Volatility**: Standard deviation of returns, measuring risk
  - **Sharpe Ratio**: Risk-adjusted return (return per unit of risk)
  - **Maximum Drawdown**: Largest peak-to-trough decline

**Why**: Helps users understand financial metrics without cluttering the UI.

### 5. Reusable Filter Hook ✅

**Files Created**: `hooks/useFactorFilters.ts`

**Changes**:
- Extracted filter state logic into custom hook
- Returns filters object, setters, clearFilters, and activeFiltersCount
- Uses `useMemo` for performance optimization

**Why**: Improves code reusability, testability, and maintainability.

### 6. Testing Infrastructure ✅

**Files Created**:
- `jest.config.js` - Jest configuration for Next.js
- `jest.setup.js` - Testing library setup
- `__tests__/utils.test.ts` - Utility function tests

**Files Modified**: `package.json`

**Changes**:
- Installed `@testing-library/react`, `@testing-library/jest-dom`, `jest`
- Configured Jest with Next.js integration
- Created comprehensive tests for `formatPercent`, `formatDate`, `getValueColor`, `formatNumber`
- Added test scripts: `npm test` and `npm test:ci`

**Why**: Ensures code quality and prevents regressions.

## Environment Setup

### Prerequisites
- Node.js 18+ 
- Python 3.13+ (for backend)
- SQLite database configured

### Environment Variables
Create `.env` in project root (already exists):
```
DATABASE_URL=sqlite:///./aqr_factors.db
```

Create `.env.local` in `frontend/` (optional):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running the Application

### Backend
```bash
# From project root
python -m uvicorn backend.main:app --reload
```
API will be available at `http://localhost:8000`

### Frontend
```bash
# From frontend directory
npm run dev
```
App will be available at `http://localhost:3000` (or 3002 if port is taken)

## Testing

### Run All Tests
```bash
cd frontend
npm test
```

### Run Tests in CI Mode
```bash
npm run test:ci
```

### Current Test Coverage
- ✅ `formatPercent()` - handles decimals, null, undefined, NaN
- ✅ `formatDate()` - formats ISO dates, handles null/undefined
- ✅ `getValueColor()` - returns correct classes for positive/negative/null
- ✅ `formatNumber()` - formats with commas, handles null/undefined

## Verification Steps

### 1. Verify Error Handling
1. Stop the backend server
2. Navigate to `/factors` page
3. **Expected**: Red error banner with "Error Loading Factors" and retry button
4. Click "Try Again"
5. **Expected**: Attempts to reload factors

### 2. Verify Loading States
1. Refresh `/factors` page
2. **Expected**: 6 skeleton cards appear briefly during loading
3. **Expected**: Skeleton cards have pulsing animation

### 3. Verify Empty States
1. Apply filters that return no results (e.g., search for "xyz123")
2. **Expected**: Empty state with icon and message "Try adjusting your filters"
3. **Expected**: "Clear All Filters" button appears
4. Click "Clear All Filters"
5. **Expected**: All filters clear and factors reload

### 4. Verify Tooltips
1. Hover over "Ann. Return" metric on any factor card
2. **Expected**: Tooltip shows "Annualized Return: Average yearly return of the factor"
3. Repeat for Volatility, Sharpe Ratio, Max DD

### 5. Verify Search Functionality
1. Type "quality" in search box
2. **Expected**: Only factors with "quality" in name/code appear
3. Type "value"
4. **Expected**: Value-related factors appear

### 6. Verify Filter Combinations
1. Select "US" region
2. **Expected**: Only US factors shown, count updates
3. Add "Monthly" frequency
4. **Expected**: Only US Monthly factors shown
5. Click "Clear All"
6. **Expected**: All filters reset

### 7. Verify Grid/Table Toggle
1. Click "Table" button
2. **Expected**: Factors display in table format with all columns
3. Click "Grid" button
4. **Expected**: Factors display in card grid

### 8. Verify Factor Count
1. Note the count "X factors found"
2. Count the actual cards/rows displayed
3. **Expected**: Numbers match exactly

## Data Mapping Verification

The Factor type interface is well-defined in `types/index.ts`:
- ✅ Returns are stored as decimals (0.08 = 8%)
- ✅ `formatPercent()` multiplies by 100 for display
- ✅ Sharpe ratio displays 2 decimals
- ✅ Dates format from ISO to readable format
- ✅ Null values display as "N/A"

## Known Limitations

1. **No Pagination**: Currently limited to 100 factors (set in API call)
   - Future: Implement client-side pagination or infinite scroll
   
2. **No Server-Side Search**: Search is backend-controlled
   - Verify backend `/api/factors?search=X` searches name AND description
   
3. **No Caching**: API calls are made on every filter change
   - Future: Implement React Query or SWR for caching

4. **No Debouncing**: Search fires on every keystroke
   - Future: Add debounce to search input

## Performance Considerations

- **Skeleton Loaders**: Reduce perceived load time
- **useMemo**: Used in `useFactorFilters` for computed values
- **Transition Classes**: Smooth animations don't block rendering
- Grid layout is CSS Grid-based, very performant

## Future Improvements

1. **Phase 6 - Performance** (if needed)
   - Add pagination when factor count > 50
   - Implement React Query for caching
   - Debounce search input
   - React.memo on FactorCard

2. **Additional Tests**
   - Component tests for FactorCard
   - Integration tests for filters page
   - Hook tests for useFactorFilters

3. **Accessibility**
   - Add ARIA labels
   - Keyboard navigation improvements
   - Focus management

4. **Advanced Features**
   - Save filter preferences to localStorage
   - Export factor list to CSV
   - Favorites/bookmarks

## Troubleshooting

### Tests Fail to Run
```bash
# Clear Jest cache
npm test -- --clearCache

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Frontend Won't Start
```bash
# Check if port 3000 is in use
# Next.js will auto-increment to 3001, 3002, etc.

# Clear Next.js cache
rm -rf .next
npm run dev
```

### Backend Errors
```bash
# Verify database exists
ls aqr_factors.db

# Check if data is loaded
python verify_data.py

# Restart backend
python -m uvicorn backend.main:app --reload
```

## Summary of Files Changed

### Created
- ✅ `frontend/components/FactorCardSkeleton.tsx`
- ✅ `frontend/hooks/useFactorFilters.ts`
- ✅ `frontend/jest.config.js`
- ✅ `frontend/jest.setup.js`
- ✅ `frontend/__tests__/utils.test.ts`

### Modified
- ✅ `frontend/pages/factors/index.tsx` - Error handling, loading states, empty states
- ✅ `frontend/components/FactorCard.tsx` - Added tooltips
- ✅ `frontend/package.json` - Added test scripts and dev dependencies

### No Changes Required
- ✅ `frontend/lib/api.ts` - Already well structured
- ✅ `frontend/types/index.ts` - Factor type already comprehensive
- ✅ `frontend/lib/utils.ts` - Already handles edge cases correctly

## Contact & Support

For questions or issues:
1. Check this document first
2. Review implementation plan in `.gemini/antigravity/brain/.../implementation_plan.md`
3. Run tests: `npm test`
4. Check browser console for errors
5. Check backend logs for API errors

---

**Last Updated**: 2025-11-19  
**Version**: 1.1.0  
**Status**: ✅ Functional improvements complete, tested, and documented
