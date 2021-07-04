from datetime import datetime
import pprint
import copy

from feature_extractor import *


class Block_Controller(object):
    # GetNextMove is main function.
    # input
    #    GameStatus : this data include all field status,
    #                 in detail see the internal GameStatus data.
    # output
    #    nextMove : this data include next shape position and the other,
    #               if return None, do nothing to nextMove.
    def GetNextMove(self, nextMove, GameStatus, BOARD_DATA):

        t1 = datetime.now()

        # print GameStatus
        print("=================================================>")
        # pprint.pprint(GameStatus, width=61, compact=True)

        #  #                   ##             ##
        # ### -> (0, 1, 2, 3)   ## -> (0, 1)  ## -> (0)
        CurrentShapeDirectionRange = GameStatus["block_info"]["currentShape"]["direction_range"]
        # Shape() クラス
        self.CurrentShape_class = GameStatus["block_info"]["currentShape"]["class"]
        NextShapeDirectionRange = GameStatus["block_info"]["nextShape"]["direction_range"]
        self.NextShape_class = GameStatus["block_info"]["nextShape"]["class"]
        # 0
        self.ShapeNone_index = GameStatus["debug_info"]["shape_info"]["shapeNone"]["index"]
        # 10列目のpeak
        col10_peak = get_peaks_per_col(BOARD_DATA)[BOARD_DATA.width - 1]
        # 9列のBOARD_DATA
        self.BOARD_DATA = copy.deepcopy(BOARD_DATA)
        backBoard2d = get_backBoard2d(self.BOARD_DATA)
        backBoard2d_9cols = backBoard2d[:, :-1]
        self.BOARD_DATA.backBoard = get_backBoard1d(backBoard2d_9cols)
        self.BOARD_DATA.width -= 1

        if self.CurrentShape_class.shape == 1 and whether_can_put_I_in(self.BOARD_DATA, col10_peak):
            strategy = (0, BOARD_DATA.width, 1, 1)
        else:
            LatestEvalValue = -100000
            strategy = (0, 5, 1, 1)
            for direction0 in CurrentShapeDirectionRange:
                x0Min, x0Max = self.getSearchXRange(self.CurrentShape_class, direction0)
                for x0 in range(x0Min, x0Max):
                    self.BOARD_DATA_tmp = self.getBoard(self.BOARD_DATA, self.CurrentShape_class, direction0, x0)
                    #print(get_backBoard2d(self.BOARD_DATA_tmp))

                    for direction1 in NextShapeDirectionRange:
                        x1Min, x1Max = self.getSearchXRange(self.NextShape_class, direction1)
                        for x1 in range(x1Min, x1Max):
                            self.BOARD_DATA_tmp2 = self.getBoard(self.BOARD_DATA_tmp, self.NextShape_class, direction1, x1)
                            # print(get_backBoard2d(self.BOARD_DATA_tmp2))

                            EvalValue = self.calcEvaluationValue(self.BOARD_DATA_tmp2)
                            #print(EvalValue)
                            if EvalValue > LatestEvalValue:
                                strategy = (direction0, x0, 1, 1)
                                LatestEvalValue = EvalValue

        # return nextMove
        print("===", datetime.now() - t1)
        nextMove["strategy"]["direction"] = strategy[0]
        nextMove["strategy"]["x"] = strategy[1]
        nextMove["strategy"]["y_operation"] = strategy[2]
        nextMove["strategy"]["y_moveblocknum"] = strategy[3]
        print(nextMove)
        return nextMove


    def getSearchXRange(self, Shape_class, direction):
        #
        # get x range from shape direction.
        #
        minX, maxX, _, _ = Shape_class.getBoundingOffsets(direction)  # get shape x offsets[minX,maxX] as relative value.
        xMin = -1 * minX
        xMax = self.BOARD_DATA.width - maxX
        return xMin, xMax


    def getShapeCoordArray(self, Shape_class, direction, x, y):
        #
        # get coordinate array by given shape.
        #
        coordArray = Shape_class.getCoords(direction, x, y) # get array from shape direction, x, y.
        return coordArray


    def getBoard(self, BOARD_DATA, Shape_class, direction, x):
        #
        # get new board.
        #
        # copy backboard data to make new board.
        # if not, original backboard data will be updated later.

        BOARD_DATA_tmp = copy.deepcopy(BOARD_DATA)
        board = self.dropDown(BOARD_DATA_tmp.backBoard, Shape_class, direction, x)
        BOARD_DATA_tmp.backBoard = board
        return BOARD_DATA_tmp


    def dropDown(self, board, Shape_class, direction, x):
        #
        # internal function of getBoard.
        # -- drop down the shape on the board.
        #
        dy = self.BOARD_DATA.height - 1
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        # update dy
        for _x, _y in coordArray:
            _yy = 0
            while _yy + _y < self.BOARD_DATA.height and (_yy + _y < 0 or board[(_y + _yy) * self.BOARD_DATA.width + _x] == self.ShapeNone_index):
                _yy += 1
            _yy -= 1
            if _yy < dy:
                dy = _yy
        # get new board
        _board = self.dropDownWithDy(board, Shape_class, direction, x, dy)
        return _board


    def dropDownWithDy(self, board, Shape_class, direction, x, dy):
        #
        # internal function of dropDown.
        #
        _board = board
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        for _x, _y in coordArray:
            _board[(_y + dy) * self.BOARD_DATA.width + _x] = Shape_class.shape
        return _board


    def calcEvaluationValue(self, BOARD_DATA):

        sum_nholes = get_sum_nholes(BOARD_DATA)
        bumpiness = get_bumpiness(BOARD_DATA)
        max_peak = get_max_peak(BOARD_DATA)
        max_well = get_max_well(BOARD_DATA)
        max_well2 = get_max_well2(BOARD_DATA)
        #print('hole: ', sum_nholes, ', bump: ', bumpiness, 'mpeak: ', max_peak, 'mwell: ', max_well, 'mwell2: ', max_well2)

        score = 0
        score -= sum_nholes * 50
        score -= bumpiness * 1
        score -= max_peak * 5
        score -= max_well * 5
        if max_well2 >= 3:
            score -= max_well2 * 20

        return score


BLOCK_CONTROLLER = Block_Controller()

"""
Currentのみ
score = 0
score -= sum_nholes * 10.0
score -= bumpiness * 1.0
score -= max_peak * 1
score -= max_well * 3
    
    ランダムじゃない
    ##### YOUR_RESULT #####
    score:18382,line:57,gameover:1,time[s]:180.005
    
    ##### SCORE DETAIL #####
      1 line: 100 * 4 = 400
      2 line: 300 * 2 = 600
      3 line: 700 * 3 = 2100
      4 line: 1300 * 10 = 13000
      dropdownscore: 2782
      gameover: : -500 * 1 = -500
    ##### ###### #####


Currentのみ
score = 0
score -= sum_nholes * 50.0
score -= bumpiness * 1.0
score -= max_peak * 1
if max_well >= 3:
    score -= max_well * 5
    
    ランダムじゃない
    ##### YOUR_RESULT #####
    score:19032,line:56,gameover:1,time[s]:180.357
    
    ##### SCORE DETAIL #####
      1 line: 100 * 1 = 100
      2 line: 300 * 1 = 300
      3 line: 700 * 3 = 2100
      4 line: 1300 * 11 = 14300
      dropdownscore: 2732
      gameover: : -500 * 1 = -500
    ##### ###### #####


CurrentとNext
score = 0
score -= sum_nholes * 50
score -= bumpiness * 1
if max_well2 >= 3:
    score -= max_well2 * 20
    
    ランダムじゃない
    ##### YOUR_RESULT #####
    score:22158,line:65,gameover:0,time[s]:180.306
    
    ##### SCORE DETAIL #####
      1 line: 100 * 1 = 100
      2 line: 300 * 0 = 0
      3 line: 700 * 4 = 2800
      4 line: 1300 * 13 = 16900
      dropdownscore: 2358
      gameover: : -500 * 0 = 0
    ##### ###### #####
    
    ランダム
    ##### YOUR_RESULT #####
    score:12557,line:36,gameover:2,time[s]:180.893
    
    ##### SCORE DETAIL #####
      1 line: 100 * 1 = 100
      2 line: 300 * 0 = 0
      3 line: 700 * 1 = 700
      4 line: 1300 * 8 = 10400
      dropdownscore: 2357
      gameover: : -500 * 2 = -1000
    ##### ###### #####
    
    ランダム
    ##### YOUR_RESULT #####
    score:17048,line:49,gameover:1,time[s]:180.475
    
    ##### SCORE DETAIL #####
      1 line: 100 * 0 = 0
      2 line: 300 * 0 = 0
      3 line: 700 * 3 = 2100
      4 line: 1300 * 10 = 13000
      dropdownscore: 2448
      gameover: : -500 * 1 = -500
    ##### ###### #####

"""
